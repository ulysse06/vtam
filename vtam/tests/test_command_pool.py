import filecmp
import os
import shlex
import subprocess
import sys

import pandas
import pathlib
import shutil
import sqlalchemy
import unittest

from vtam.models.Biosample import Biosample
from vtam.models.FilterChimeraBorderline import FilterChimeraBorderline
from vtam.models.FilterCodonStop import FilterCodonStop
from vtam.models.Marker import Marker
from vtam.models.Run import Run
from vtam.models.SampleInformation import SampleInformation
from vtam.models.Variant import Variant
from vtam.utils.PathManager import PathManager


class TestAsvtableRunner(unittest.TestCase):

    """Will test main commands based on a complete test dataset"""

    def setUp(self):

        # vtam needs to be in the tsv_path
        subprocess.run([sys.executable, '-m', 'pip', 'install', '{}/.'.format(PathManager.get_package_path()),
                        '--upgrade'])

        self.package_path = os.path.join(PathManager.get_package_path())
        self.test_path = PathManager.get_test_path()
        self.outdir_path = os.path.join(self.test_path, 'outdir')
        # during development of the test, this prevents errors
        shutil.rmtree(self.outdir_path, ignore_errors=True)
        pathlib.Path(self.outdir_path).mkdir(parents=True, exist_ok=True)

        self.args = {}
        self.args['runmarker'] = os.path.join(self.package_path, "doc/data/pool_run_marker.tsv")
        self.args['db'] = os.path.join(self.outdir_path, "db.sqlite")
        self.args['asvtable_pooled_default'] = os.path.join(self.outdir_path, "asvtable_pooled_default.tsv")
        self.args['asvtable_pooled_default_bak'] = os.path.join(self.test_path, "test_files_dryad.f40v5_small/run1_mfzr_zfzr/asvtable_pooled_default.tsv")

        ############################################################################################
        #
        # Init DB
        #
        ############################################################################################

        filter_codon_stop_path = os.path.join(
            self.test_path, "test_files_dryad.f40v5_small/run1_mfzr_zfzr/filter_codon_stop.tsv")
        variant_path = os.path.join(
            self.test_path, "test_files_dryad.f40v5_small/run1_mfzr_zfzr/variant_filter_codon_stop.tsv")
        sample_information_path = os.path.join(
            self.test_path, "test_files_dryad.f40v5_small/run1_mfzr_zfzr/sample_information.tsv")

        self.engine = sqlalchemy.create_engine('sqlite:///{}'.format(self.args['db']), echo=False)

        sample_information_df = pandas.read_csv(sample_information_path, sep="\t", header=0)
        sample_information_df.to_sql(name=SampleInformation.__tablename__, con=self.engine.connect())

        run_df = pandas.DataFrame({'name': ['run1']}, index=range(1, 2))
        run_df.to_sql(name=Run.__tablename__, con=self.engine.connect(), index_label='id')

        marker_df = pandas.DataFrame({'name': ['MFZR', 'ZFZR']}, index=range(1, 3))
        marker_df.to_sql(name=Marker.__tablename__, con=self.engine.connect(), index_label='id')

        biosample_df = pandas.DataFrame({'name': ['tpos1_run1', 'tnegtag_run1', '14ben01', '14ben02']}, index=range(1, 5))
        biosample_df.to_sql(name=Biosample.__tablename__, con=self.engine.connect(), index_label='id')

        variant_df = pandas.read_csv(variant_path, sep="\t", header=0, index_col='id')
        variant_df.to_sql(name=Variant.__tablename__, con=self.engine.connect(), index_label='id')

        filter_codon_stop_df = pandas.read_csv(filter_codon_stop_path, sep="\t", header=0)
        filter_codon_stop_df.to_sql(name=FilterCodonStop.__tablename__, con=self.engine.connect())

        filter_chimera_borderline_path = os.path.join(
            self.test_path, "test_files_dryad.f40v5_small/run1_mfzr_zfzr/filter_chimera_borderline_and_filter_codon_stop.tsv")
        filter_chimera_borderline_db = pandas.read_csv(filter_chimera_borderline_path, sep="\t", header=0)
        filter_chimera_borderline_db.to_sql(name=FilterChimeraBorderline.__tablename__, con=self.engine.connect())

        self.biosample_list = ['tpos1_run1', 'tnegtag_run1', '14ben01', '14ben02']


    def test_command_pool(self):

        command = "vtam pool --runmarker {runmarker} --db {db} --output {asvtable_pooled_default}".format(**self.args)
        subprocess.run(shlex.split(command), check=True)

        self.assertTrue(filecmp.cmp(self.args['asvtable_pooled_default'], self.args['asvtable_pooled_default_bak'], shallow=True))

    def tearDown(self):
        shutil.rmtree(self.outdir_path, ignore_errors=True)
