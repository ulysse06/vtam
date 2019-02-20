import pandas
from unittest import TestCase
from wopmetabarcoding.wrapper.FilterUtilities import FilterRunner

class TestFilter(TestCase):
    def setUp(self):
        self.variant_df = pandas.DataFrame({
            'id':[1,22],
            'sequence_':["tata", "tgtg"],
        })
        self.variant_read_count_df = pandas.DataFrame({
            'variant_id': [1]*6 + [12]*6 + [9]*6 +[22]*6 ,
            'biosample_id':[1,1,1,2,2,2,1,1,1,2,2,2,1,1,1,2,2,2,1,1,1,2,2,2],
            'replicate_id':[1,2,3,1,2,3,1,2,3,1,2,3,1,2,3,1,2,3,1,2,3,1,2,3],
            'read_count':[
                10,5,0,249,58,185,
                0,0,2,598,50,875,
                125,214,20,1284,1798,1913,
                25,58,23,10980,8999,13814,
            ],
        })
        self.marker_id = 1
        #
        self.filter_runner = FilterRunner(self.variant_df, self.variant_read_count_df, self.marker_id)

    def test_02_f2_lfn2_per_variant_mekdad(self):
        lfn_var_threshold = 0.001
        self.filter_runner.f2_lfn2_per_variant_mekdad(lfn_var_threshold)
        #
        self.assertTrue(not self.filter_runner.passed_variant_mekdad_df.loc[(self.filter_runner.passed_variant_mekdad_df.variant_id==22)
                                                                        & (self.filter_runner.passed_variant_mekdad_df.biosample_id==1)
                                                                        & (self.filter_runner.passed_variant_mekdad_df.replicate_id==1)
                                                                        & (self.filter_runner.passed_variant_mekdad_df.filter_name=='f2_lfn2_per_variant_mekdad'),
                                                                        'filter_passed'].values[0])
        self.assertTrue(self.filter_runner.passed_variant_mekdad_df.loc[(self.filter_runner.passed_variant_mekdad_df.variant_id==22)
                                                                        & (self.filter_runner.passed_variant_mekdad_df.biosample_id==1)
                                                                        & (self.filter_runner.passed_variant_mekdad_df.replicate_id==2)
                                                                        & (self.filter_runner.passed_variant_mekdad_df.filter_name=='f2_lfn2_per_variant_mekdad'),
                                                                        'filter_passed'].values[0])
        self.assertTrue(not self.filter_runner.passed_variant_mekdad_df.loc[(self.filter_runner.passed_variant_mekdad_df.variant_id==22)
                                                                        & (self.filter_runner.passed_variant_mekdad_df.biosample_id==1)
                                                                        & (self.filter_runner.passed_variant_mekdad_df.replicate_id==3)
                                                                        & (self.filter_runner.passed_variant_mekdad_df.filter_name=='f2_lfn2_per_variant_mekdad'),
                                                                        'filter_passed'].values[0])


    def test_03_f3_lfn2_per_replicate_series_mekdad(self):
        lfn_var_threshold = 0.005
        self.filter_runner.f3_lfn2_per_replicate_series_mekdad(lfn_var_threshold)
        #
        self.assertTrue(not self.filter_runner.passed_variant_mekdad_df.loc[
                            (self.filter_runner.passed_variant_mekdad_df.variant_id == 12)
                            & (self.filter_runner.passed_variant_mekdad_df.biosample_id == 1)
                            & (self.filter_runner.passed_variant_mekdad_df.replicate_id == 3)
                            & (self.filter_runner.passed_variant_mekdad_df.filter_name == 'f3_lfn2_per_replicate_series_mekdad'),
                            'filter_passed'].values[0])
        self.assertTrue(self.filter_runner.passed_variant_mekdad_df.loc[
                            (self.filter_runner.passed_variant_mekdad_df.variant_id == 12)
                            & (self.filter_runner.passed_variant_mekdad_df.biosample_id == 2)
                            & (self.filter_runner.passed_variant_mekdad_df.replicate_id == 3)
                            & (self.filter_runner.passed_variant_mekdad_df.filter_name == 'f3_lfn2_per_replicate_series_mekdad'),
                            'filter_passed'].values[0])


    def test_04_f4_lfn3_read_count_mekdad(self):
        lfn_read_count_threshold = 10

        self.filter_runner.f4_lfn3_read_count_mekdad(lfn_read_count_threshold)
        #import pdb;
        #pdb.set_trace()

        self.assertTrue(not self.filter_runner.passed_variant_mekdad_df.loc[
            (self.filter_runner.passed_variant_mekdad_df.variant_id == 12)
            & (self.filter_runner.passed_variant_mekdad_df.biosample_id == 1)
            & (self.filter_runner.passed_variant_mekdad_df.replicate_id == 1)
            & (self.filter_runner.passed_variant_mekdad_df.filter_name == 'f4_lfn3_read_count_mekdad'),
            'filter_passed'].values[0])
        self.assertTrue(self.filter_runner.passed_variant_mekdad_df.loc[
                            (self.filter_runner.passed_variant_mekdad_df.variant_id == 12)
                            & (self.filter_runner.passed_variant_mekdad_df.biosample_id == 2)
                            & (self.filter_runner.passed_variant_mekdad_df.replicate_id == 3)
                            & ( self.filter_runner.passed_variant_mekdad_df.filter_name == 'f4_lfn3_read_count_mekdad'),
                            'filter_passed'].values[0])
        self.assertTrue(self.filter_runner.passed_variant_mekdad_df.loc[
                            (self.filter_runner.passed_variant_mekdad_df.variant_id == 1)
                            & (self.filter_runner.passed_variant_mekdad_df.biosample_id == 1)
                            & (self.filter_runner.passed_variant_mekdad_df.replicate_id == 2)
                            & (self.filter_runner.passed_variant_mekdad_df.filter_name == 'f4_lfn3_read_count_mekdad'),
                            'filter_passed'].values[0] == False)

    def test_05_f5_lfn2_var_dep_mekdad(self):
        lfn_per_var = {9: 0.05, 22: 0.01, 0: 0}


        self.filter_runner.f5_lfn2_var_dep_mekdad(self)(lfn_per_var)

        self.assertTrue(not self.filter_runner.passed_variant_mekdad_df.loc[
                            (self.filter_runner.passed_variant_mekdad_df.variant_id == 9)
                            & (self.filter_runner.passed_variant_mekdad_df.biosample_id == 1)
                            & (self.filter_runner.passed_variant_mekdad_df.replicate_id == 2)
                            & (self.filter_runner.passed_variant_mekdad_df.filter_name == 'f5_lfn2_var_dep_mekdad'),
                            'filter_passed'].values[0])
        self.assertTrue(not self.filter_runner.passed_variant_mekdad_df.loc[
                            (self.filter_runner.passed_variant_mekdad_df.variant_id == 22)
                            & (self.filter_runner.passed_variant_mekdad_df.biosample_id == 1)
                            & (self.filter_runner.passed_variant_mekdad_df.replicate_id == 2)
                            & (self.filter_runner.passed_variant_mekdad_df.filter_name == 'f5_lfn2_var_dep_mekdad'),
                            'filter_passed'].values[0] == False)