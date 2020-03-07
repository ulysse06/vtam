# -*- coding: utf-8 -*-
import pathlib

from vtam.utils.PathManager import PathManager
from vtam.CommandTaxonomy import CommandTaxonomy
from vtam.utils.Logger import Logger
from vtam.utils.VariantDFutils import VariantDFutils
from vtam.utils.TaxAssignRunner import f06_select_ltg, f07_blast_result_to_ltg_tax_id
from unittest import TestCase

import inspect
import numpy
import os
import pandas


class TestTaxAssign(TestCase):

    def setUp(self):
        #####################################
        #
        # Download taxonomy.tsv
        #
        #####################################
        #
        self.ltg_rule_threshold = 97
        self.min_number_of_taxa = 3
        self.include_prop = 90
        #
        self.__testdir_path = os.path.join(PathManager.get_test_path())
        self.lblast_output_var3_tsv = os.path.join(PathManager.get_test_path(), self.__testdir_path, "test_files", "lblast_output_var3.tsv")
        self.lblast_output_var7_tsv = os.path.join(PathManager.get_test_path(), self.__testdir_path, "test_files", "lblast_output_var7.tsv")
        self.lblast_output_var9_tsv = os.path.join(PathManager.get_test_path(), self.__testdir_path, "test_files", "lblast_output_var9.tsv")
        self.tax_lineage_variant13_tsv = os.path.join(PathManager.get_test_path(), self.__testdir_path, "test_files", "tax_lineage_variant13.tsv")

    @classmethod
    def setUpClass(cls):
        """ get_some_resource() is slow, to avoid calling it for each tests use setUpClass()
            and store the result as class variable
        """
        super(TestTaxAssign, cls).setUpClass()
        # create_vtam_data_dir()
        taxonomydb = CommandTaxonomy(precomputed=True)
        taxonomy_tsv_path = taxonomydb.get_path()
        #
        # cls.taxonomy_df = f01_taxonomy_tsv_to_df(taxonomy_tsv_path)
        cls.taxonomy_db_df = pandas.read_csv(taxonomy_tsv_path, sep="\t", header=0,
                                         dtype={'tax_id': 'int', 'parent_tax_id': 'int', 'old_tax_id': 'float'})


    def test_variant_df_to_fasta(self):
        variant_dic = {
            'id' : [57, 107],
            'sequence' : ['ACTATATTTTATTTTTGGGGCTTGATCCGGAATGCTGGGCACCTCTCTAAGCCTTCTAATTCGTGCCGAGCTGGGGCACCCGGGTTCTTTAATTGGCGACGATCAAATTTACAATGTAATCGTCACAGCCCATGCTTTTATTATGATTTTTTTCATGGTTATGCCTATTATAATC'
                                  , 'ACTTTATTTCATTTTCGGAACATTTGCAGGAGTTGTAGGAACTTTACTTTCATTATTTATTCGTCTTGAATTAGCTTATCCAGGAAATCAATTTTTTTTAGGAAATCACCAACTTTATAATGTGGTTGTGACAGCACATGCTTTTATCATGATTTTTTTCATGGTTATGCCGATTTTAATC']
        }
        variant_df = pandas.DataFrame(data=variant_dic)
        variant_df.set_index('id', inplace=True)

        #
        Logger.instance().debug(
            "file: {}; line: {}; Create SortedReadFile from Variants".format(__file__, inspect.currentframe().f_lineno ,'PoolMarkers'))
        this_tempdir = os.path.join(PathManager.instance().get_tempdir(), os.path.basename(__file__))
        pathlib.Path(this_tempdir).mkdir(exist_ok=True)
        variant_fasta = os.path.join(this_tempdir, 'variant.fasta')
        variant_df_utils = VariantDFutils(variant_df)
        variant_df_utils.to_fasta(fasta_path=variant_fasta)
        #
        variant_fasta_content_expected =""">57\nACTATATTTTATTTTTGGGGCTTGATCCGGAATGCTGGGCACCTCTCTAAGCCTTCTAATTCGTGCCGAGCTGGGGCACCCGGGTTCTTTAATTGGCGACGATCAAATTTACAATGTAATCGTCACAGCCCATGCTTTTATTATGATTTTTTTCATGGTTATGCCTATTATAATC\n>107\nACTTTATTTCATTTTCGGAACATTTGCAGGAGTTGTAGGAACTTTACTTTCATTATTTATTCGTCTTGAATTAGCTTATCCAGGAAATCAATTTTTTTTAGGAAATCACCAACTTTATAATGTGGTTGTGACAGCACATGCTTTTATCATGATTTTTTTCATGGTTATGCCGATTTTAATC\n"""
        with open(variant_fasta, 'r') as fin:
            variant_fasta_content = fin.read()
        self.assertTrue(variant_fasta_content_expected == variant_fasta_content)

    def test_f03_1_tax_id_to_taxonomy_lineage(self):
        tax_id = 183142
        #
        # TODO fix this tests
        # taxonomy_lineage_dic = f04_1_tax_id_to_taxonomy_lineage(tax_id, TestTaxAssign.taxonomy_db_df)
        # self.assertTrue({'tax_id': 183142, 'species': 183142, 'genus': 10194, 'family': 10193, 'order': 84394,
        #                  'superorder': 1709201, 'class': 10191, 'phylum': 10190, 'no rank': 131567, 'kingdom': 33208,
        #                  'superkingdom': 2759} == taxonomy_lineage_dic)

    # def test_f05_blast_result_subset(self):
    #     # From
    #     # 'variant_id': 'MFZR_001274',
    #     # 'variant_sequence': 'TTTATACTTTATTTTTGGTGTTTGAGCCGGAATAATTGGCTTAAGAATAAGCCTGCTAATCCGTTTAGAGCTTGGGGTTCTATGACCCTTCCTAGGAGATGAGCATTTGTACAATGTCATCGTTACCGCTCATGCTTTTATCATAATTTTTTTTATGGTTATTCCAATTTCTATA',
    #     qblast_out_dic = {
    #         'target_id': [514884684, 514884680],
    #         'identity': [80, 80],
    #         'target_tax_id': [1344033, 1344033]}
    #     qblast_result_subset_df = pandas.DataFrame(data=qblast_out_dic)
    #     tax_lineage_df = f05_blast_result_subset(qblast_result_subset_df, TestTaxAssign.taxonomy_db_df)
    #     self.assertTrue(tax_lineage_df.to_dict('list')=={'identity': [80, 80], 'class': [10191, 10191],
    #         'family': [204743, 204743], 'genus': [360692, 360692], 'kingdom': [33208, 33208],
    #         'no rank': [131567, 131567], 'order': [84394, 84394], 'phylum': [10190, 10190],
    #         'species': [1344033, 1344033], 'superkingdom': [2759, 2759], 'superorder': [1709201, 1709201], 'tax_id': [1344033, 1344033]})

    def test_f06_select_ltg_identity_80(self):
        # List of lineages that will correspond to list of tax_ids: One lineage per row
        tax_lineage_df = pandas.DataFrame(data={
            'species' : [666, 183142, 183142, 183142],
            'genus' : [10194, 10194, 10194, 10194],
            'order' : [10193, 10193, 10193, 10193],
            'superorder' : [84394, 84394, 84394, 84394],
        })
        identity = 80
        ltg_tax_id, ltg_rank = f06_select_ltg(tax_lineage_df=tax_lineage_df, include_prop=self.include_prop)
        #
        # import pdb; pdb.set_trace()
        self.assertTrue(ltg_tax_id == 10194)
        self.assertTrue(ltg_rank == 'genus')

    def test_f06_select_ltg_column_none(self):
        # List of lineages that will correspond to list of tax_ids: One lineage per row
        tax_lineage_df = pandas.DataFrame(data={
            'species' : [666, 183142, 183142, 183142],
            'subgenus' : [numpy.nan] * 4,
            'genus' : [10194, 10194, 10194, 10194],
            'order' : [10193, 10193, 10193, 10193],
            'superorder' : [84394, 84394, 84394, 84394],
        })
        #
        identity = 80
        #
        ltg_tax_id, ltg_rank = f06_select_ltg(tax_lineage_df=tax_lineage_df, include_prop=self.include_prop)
        #
        self.assertTrue(ltg_tax_id == 10194)
        self.assertTrue(ltg_rank == 'genus')

    def test_f05_select_ltg_identity_100(self):
        # List of lineages that will correspond to list of tax_ids: One lineage per row
        tax_lineage_df = pandas.DataFrame(data={
            'species' : [666, 183142, 183142, 183142],
            'genus' : [10194, 10194, 10194, 10194],
            'order' : [10193, 10193, 10193, 10193],
            'superorder' : [84394, 84394, 84394, 84394],
        })
        identity = 100
        #
        ltg_tax_id, ltg_rank = f06_select_ltg(tax_lineage_df=tax_lineage_df, include_prop=self.include_prop)
        #
        self.assertTrue(ltg_tax_id == 10194)
        self.assertTrue(ltg_rank == 'genus')

    def test_f05_f06_var7_identity100(self):
        """
        This tests takes a local blast results of a single variant with variant_id, target_id, identity, evalue, coveration and target_tax_id
        and returns the ltg_tax_id and ltg_rank
        """
        #
        blast_output_df = pandas.read_csv(self.lblast_output_var3_tsv, sep='\t', header=None,
                                          names=['variant_id', 'target_id', 'identity', 'evalue', 'coverage',
                                                 'target_tax_id'])        #
        identity = 100
        blast_result_subset_df = blast_output_df.loc[blast_output_df.identity >= identity, ['target_id', 'target_tax_id']]
        # TODO Fix this tests. Maybe need to reorganize TaxAssignRunner
        # tax_lineage_df = f05_blast_result_subset(blast_output_df, TestTaxAssign.taxonomy_db_df)
        # ltg_tax_id, ltg_rank = f06_select_ltg(tax_lineage_df=tax_lineage_df, include_prop=self.include_prop)
        # #
        # # Outputs
        # self.assertTrue(ltg_tax_id==189839)
        # self.assertTrue(ltg_rank=='species')


    def test_f05_f06_var9_identity99(self):
        """
        This tests takes a local blast results of a single variant with variant_id, target_id, identity, evalue, coveration and target_tax_id
        and returns the ltg_tax_id and ltg_rank
        """
        #
        # Inputs
        lblast_output_tsv = self.lblast_output_var9_tsv
        identity = 99
        #
        blast_output_df = pandas.read_csv(lblast_output_tsv, sep='\t', header=None,
                                          names=['variant_id', 'target_id', 'identity', 'evalue', 'coverage',
                                                 'target_tax_id'])        #
        blast_result_subset_df = blast_output_df.loc[blast_output_df.identity >= identity, ['target_id', 'target_tax_id']]
        # TODO Fix this tests. Maybe need to reorganize TaxAssignRunner
        # tax_lineage_df = f05_blast_result_subset(blast_result_subset_df, TestTaxAssign.taxonomy_db_df)
        # ltg_tax_id, ltg_rank = f06_select_ltg(tax_lineage_df=tax_lineage_df, include_prop=self.include_prop)
        # #
        # # Outputs
        # self.assertTrue(ltg_tax_id==1077837)
        # self.assertTrue(ltg_rank=='species')


    def test_f07_var3_var7_var9(self):
        """
        This tests takes a local blast results of several variants and identities
        with variant_id, target_id, identity, evalue, coveration and target_tax_id
        and returns the resulting data
        """
        #
        # Inputs
        lblast_output_var3_tsv = self.lblast_output_var3_tsv
        lblast_output_var7_tsv = self.lblast_output_var7_tsv
        lblast_output_var9_tsv = self.lblast_output_var9_tsv
        #
        lblast_output_var3_df = pandas.read_csv(lblast_output_var3_tsv, sep='\t', header=None,
                                          names=['variant_id', 'target_id', 'identity', 'evalue', 'coverage',
                                                 'target_tax_id'])
        lblast_output_var7_df = pandas.read_csv(lblast_output_var7_tsv, sep='\t', header=None,
                                          names=['variant_id', 'target_id', 'identity', 'evalue', 'coverage',
                                                 'target_tax_id'])
        lblast_output_var9_df = pandas.read_csv(lblast_output_var9_tsv, sep='\t', header=None,
                                          names=['variant_id', 'target_id', 'identity', 'evalue', 'coverage',
                                                 'target_tax_id'])
        #
        # Input processing
        lblast_output_df = pandas.concat([lblast_output_var3_df, lblast_output_var7_df, lblast_output_var9_df], axis=0)
        lblast_output_df = lblast_output_df[['variant_id', 'identity', 'target_tax_id']]
        #
        # Run
        # TODO replace this tests
        # lineage_list = []
        # for target_tax_id in lblast_output_df.target_tax_id.unique().tolist():
        #     lineage_list.append(f04_1_tax_id_to_taxonomy_lineage(target_tax_id, TestTaxAssign.taxonomy_db_df))
        # tax_id_to_lineage_df = pandas.DataFrame(lineage_list)
        # #
        # # Merge lblast output with tax_id_to_lineage_df
        # variantid_identity_lineage_df = lblast_output_df.merge(tax_id_to_lineage_df, left_on='target_tax_id',
        #                                                        right_on='tax_id')
        # variantid_identity_lineage_df.drop('tax_id', axis=1, inplace=True)
        # #
        # ltg_df = f07_blast_result_to_ltg_tax_id(variantid_identity_lineage_df, ltg_rule_threshold=self.ltg_rule_threshold,
        #                                         include_prop=self.include_prop, min_number_of_taxa=self.min_number_of_taxa)
        # #
        # # Output
        # self.assertTrue(ltg_df.to_dict() == {'identity': {0: 100, 1: 100, 2: 99}, 'ltg_rank': {0: 'species', 1: 'species', 2: 'species'},
        #  'ltg_tax_id': {0: 189839, 1: 1077837, 2: 1077837}, 'variant_id': {0: 3, 1: 7, 2: 9}})
