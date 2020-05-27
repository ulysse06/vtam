import pandas

from vtam.models.Biosample import Biosample
from vtam.models.Marker import Marker
from vtam.models.Run import Run
from vtam.utils.FilterPCRerrorRunner import FilterPCRerrorRunner
from vtam.utils.NameIdConverter import NameIdConverter


class OptimizePCRerrorRunner:
    """Algorithm:

    1. Run algorithm per run-marker-biosample
    2. Take 'keep' variants in 'mock' biosamples: N_i(expected)j
    3. Take all non-'keep' variants with one single nucleotide difference to the keep variants in the same 'mock' biosamples: N_i(unexpected)j
    3. Compute ratio: N_i(unexpected)j/N_i(expected)j"""

    def __init__(self, variant_read_count_df, known_occurrences_df):

        self.variant_read_count_df = variant_read_count_df
        # works only with mock biosamples
        self.known_occurrences_df = known_occurrences_df.loc[
            (known_occurrences_df.mock == 1) & (known_occurrences_df.action == 'keep'), ]

    def get_optimize_df(self, engine):

        ############################################################################################
        #
        # Group and run_name this genetic_code by run_name/marker_name combination
        # Loop by run_name/marker_name
        #
        ############################################################################################

        optimize_df = pandas.DataFrame()

        # variant_df = pandas.read_sql(sqlalchemy.select([
        #     Variant.__table__.c.id, Variant.__table__.c.sequence]), con=engine.connect(),
        #     index_col='id')

        known_occurrences_df = self.known_occurrences_df.loc[self.known_occurrences_df.mock==1, ]

        known_occurrences_run_marker_biosample_df = self.known_occurrences_df[
            ['run_id', 'marker_id', 'biosample_id']].drop_duplicates()
        for row in known_occurrences_run_marker_biosample_df.itertuples():

            run_id = row.run_id
            marker_id = row.marker_id
            biosample_id = row.biosample_id

            sequence_expected = known_occurrences_df.loc[(known_occurrences_df.run_id == run_id) & (
                        known_occurrences_df.marker_id == marker_id) & (
                                         known_occurrences_df.biosample_id == biosample_id) & (
                                         known_occurrences_df.action == 'keep'), 'variant_sequence']

            variant_expected = NameIdConverter(id_name_or_sequence_list=sequence_expected,
                                               engine=engine).variant_sequence_to_id()

            variant_expected_df = pandas.DataFrame({'sequence': sequence_expected.tolist()}, index=variant_expected)

            variant_read_count_per_biosample_df = self.variant_read_count_df.loc[
                (self.variant_read_count_df.run_id == run_id) & (
                        self.variant_read_count_df.marker_id == marker_id) & (
                            self.variant_read_count_df.biosample_id == biosample_id)]

            variant_unexpected = variant_read_count_per_biosample_df.variant_id[~variant_read_count_per_biosample_df.variant_id.isin(variant_expected)].unique()

            sequence_unexpected = NameIdConverter(id_name_or_sequence_list=variant_unexpected.tolist(),
                                               engine=engine).variant_id_to_sequence()

            variant_unexpected_df = pandas.DataFrame({'sequence': sequence_unexpected}, index=variant_unexpected)

            ########################################################################################
            #
            # Run vsearch and get alignement variant_read_count_input_df
            #
            ########################################################################################

            filter_pcr_error_runner = FilterPCRerrorRunner(
                variant_expected_df=variant_expected_df, variant_unexpected_df=variant_unexpected_df,
                variant_read_count_df=variant_read_count_per_biosample_df)

            pcr_error_df = filter_pcr_error_runner.get_variant_unexpected_to_expected_ratio_df()

            optimize_df = pandas.concat(
                [optimize_df, pcr_error_df], axis=0)

        return optimize_df


    def to_tsv(self, optimize_path, engine):

        optimize_df = self.get_optimize_df(engine=engine)

        ############################################################################################
        #
        # Convert run_id, marker_id and biosample_id to their names
        #
        ############################################################################################

        optimize_df['run'] = NameIdConverter(optimize_df.run_id.tolist(),
                                                     engine).to_names(Run)
        optimize_df['marker'] = NameIdConverter(optimize_df.marker_id.tolist(),
                                                        engine).to_names(Marker)
        optimize_df['biosample'] = NameIdConverter(
            optimize_df.biosample_id.tolist(), engine).to_names(Biosample)
        optimize_df['sequence_expected'] = NameIdConverter(
            optimize_df.variant_id_expected.tolist(), engine).variant_id_to_sequence()
        optimize_df['sequence_unexpected'] = NameIdConverter(
            optimize_df.variant_id_unexpected.tolist(), engine).variant_id_to_sequence()

        optimize_df.drop(['run_id', 'marker_id', 'biosample_id'], axis=1, inplace=True)

        ############################################################################################
        #
        # Rename and order columns and write to TSV
        #
        ############################################################################################

        optimize_df.rename({'run_name': 'run_id',
                                    'marker_name': 'marker_id',
                                    'variant_id_expected': 'variant_expected',
                                    'variant_id_unexpected': 'variant_unexpected'}, axis=1,
                                   inplace=True)
        optimize_df = optimize_df[['run', 'marker', 'biosample', 'variant_expected',
                                                   'N_ij_expected', 'variant_unexpected',
                                                   'N_ij_unexpected',
                                                   'N_ij_unexpected_to_expected_ratio',
                                                   'sequence_expected',
                                                   'sequence_unexpected']]

        # lines should be ordered: by run_name, marker_name, ...
        optimize_df.sort_values(by=['run',
                                           'marker',
                                           'N_ij_unexpected_to_expected_ratio',
                                           'variant_expected',
                                           'variant_unexpected'],
                                       ascending=[True,
                                                  True,
                                                  False,
                                                  True,
                                                  True],
                                       inplace=True)

        optimize_df.to_csv(optimize_path, header=True, sep='\t', float_format='%.8f', index=False)
