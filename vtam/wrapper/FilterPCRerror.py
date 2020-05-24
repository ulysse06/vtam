from wopmars.models.ToolWrapper import ToolWrapper
from vtam import Logger
from vtam.utils.FilterPCRerrorRunner import FilterPCRerrorRunner
from vtam.utils.SampleInformationFile import SampleInformationFile
from vtam.utils.VariantReadCountLikeDF import VariantReadCountLikeDF
from vtam.utils.VariantReadCountLikeTable import VariantReadCountLikeTable
from vtam.utils.PathManager import PathManager
from vtam.utils.VTAMexception import VTAMexception

import os
import pandas
import pathlib
import sys


class FilterPCRerror(ToolWrapper):
    __mapper_args__ = {
        "polymorphic_identity": "vtam.wrapper.FilterPCRerror"
    }

    # Input file
    __input_file_readinfo = "readinfo"
    # Input table
    __input_table_marker = "Marker"
    __input_table_run = "Run"
    __input_table_biosample = "Biosample"
    __input_table_variant = "Variant"
    __input_table_filter_min_replicate_number = "FilterMinReplicateNumber"
    # Output table
    __output_table_filter_pcr_error = "FilterPCRerror"

    def specify_input_file(self):
        return[
            FilterPCRerror.__input_file_readinfo,

        ]

    def specify_input_table(self):
        return [
            FilterPCRerror.__input_table_marker,
            FilterPCRerror.__input_table_run,
            FilterPCRerror.__input_table_biosample,
            FilterPCRerror.__input_table_variant,
            FilterPCRerror.__input_table_filter_min_replicate_number,
        ]

    def specify_output_table(self):
        return [
            FilterPCRerror.__output_table_filter_pcr_error,
        ]

    def specify_params(self):
        return {
            "pcr_error_var_prop": "float",
        }

    def run(self):
        session = self.session
        engine = session._session().get_bind()

        this_temp_dir = os.path.join(
            PathManager.instance().get_tempdir(),
            os.path.basename(__file__))
        pathlib.Path(this_temp_dir).mkdir(exist_ok=True)

        ############################################################################################
        #
        # Wrapper inputs, outputs and parameters
        #
        ############################################################################################
        #
        # Input file output
        fasta_info_tsv = self.input_file(FilterPCRerror.__input_file_readinfo)
        #
        # Input table models
        input_filter_min_replicate_model = self.input_table(
            FilterPCRerror.__input_table_filter_min_replicate_number)
        #
        # Options
        pcr_error_var_prop = self.option("pcr_error_var_prop")
        #
        # Output table models
        output_filter_pcr_error_model = self.output_table(
            FilterPCRerror.__output_table_filter_pcr_error)

        ############################################################################################
        #
        # 1. Read readinfo to get run_id, marker_id, biosample_id, replicate for current analysis
        # 2. Delete marker_name/run_name/biosample/replicate from variant_read_count_model
        # 3. Get nijk_df input
        #
        ############################################################################################

        sample_info_tsv_obj = SampleInformationFile(tsv_path=fasta_info_tsv)

        sample_info_tsv_obj.delete_from_db(
            engine=engine, variant_read_count_like_model=output_filter_pcr_error_model)

        variant_read_count_df = sample_info_tsv_obj.get_nijk_df(
            variant_read_count_like_model=input_filter_min_replicate_model,
            engine=engine,
            filter_id=None)

        ############################################################################################
        #
        # Run per biosample_id
        #
        ############################################################################################

        variant_df = sample_info_tsv_obj.get_variant_df(
            variant_read_count_like_model=input_filter_min_replicate_model, engine=engine)

        record_list = []

        run_marker_biosample_df = variant_read_count_df[[
            'run_id', 'marker_id', 'biosample_id']].drop_duplicates()
        for row in run_marker_biosample_df.itertuples():
            run_id = row.run_id
            marker_id = row.marker_id
            biosample_id = row.biosample_id

            variant_read_count_per_biosample_df = variant_read_count_df.loc[(variant_read_count_df.run_id == run_id) & (
                variant_read_count_df.marker_id == marker_id) & (variant_read_count_df.biosample_id == biosample_id)]

            variant_per_biosample_df = variant_df.loc[variant_df.index.isin(
                variant_read_count_df.variant_id.unique().tolist())]
            this_step_tmp_per_biosample_dir = os.path.join(
                this_temp_dir, "run_{}_marker_{}_biosample{}".format(
                    run_id, marker_id, biosample_id))
            pathlib.Path(this_step_tmp_per_biosample_dir).mkdir(exist_ok=True)

            ########################################################################################
            #
            # Run vsearch and get alignement variant_read_count_input_df
            #
            ########################################################################################

            filter_pcr_error_runner = FilterPCRerrorRunner(
                variant_expected_df=variant_per_biosample_df,
                variant_unexpected_df=variant_per_biosample_df,
                variant_read_count_df=variant_read_count_per_biosample_df)
            filter_output_per_biosample_df = filter_pcr_error_runner.get_variant_read_count_delete_df(
                pcr_error_var_prop)

            ########################################################################################
            #
            # Per biosample add to record list
            #
            ########################################################################################

            record_per_biosample_list = VariantReadCountLikeTable.filter_delete_df_to_dict(
                filter_output_per_biosample_df)
            record_list = record_list + record_per_biosample_list

        variant_read_count_delete_df = pandas.DataFrame.from_records(
            data=record_list)

        ############################################################################################
        #
        # 5. Write to DB
        # 6. Touch output tables, to update modification date
        # 7. Exit vtam if all variants delete
        #
        #######################################################################

        VariantReadCountLikeDF(variant_read_count_delete_df).to_sql(
            engine=engine, variant_read_count_like_model=output_filter_pcr_error_model)

        for output_table_i in self.specify_output_table():
            declarative_meta_i = self.output_table(output_table_i)
            obj = session.query(declarative_meta_i).order_by(
                declarative_meta_i.id.desc()).first()
            session.query(declarative_meta_i).filter_by(
                id=obj.id).update({'id': obj.id})
            session.commit()

        if variant_read_count_delete_df.filter_delete.sum(
        ) == variant_read_count_delete_df.shape[0]:
            Logger.instance().warning(
                VTAMexception(
                    "This filter has deleted all the variants: {}. "
                    "The analysis will stop here.".format(
                        self.__class__.__name__)))
            sys.exit(0)
