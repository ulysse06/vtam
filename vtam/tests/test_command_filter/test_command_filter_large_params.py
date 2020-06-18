import filecmp
import os
import pathlib
import shlex
import shutil
import subprocess
import sys
import tarfile
import unittest
import urllib

from vtam.utils.PathManager import PathManager
from vtam.utils.constants import sorted_dryad_f40v5_tar_gz_url
from urllib import request

@unittest.skipIf(request.urlopen(sorted_dryad_f40v5_tar_gz_url).getcode() != 200,
                 "This test requires an internet connection!")
class TestCommandsFilterParams(unittest.TestCase):

    """Will test main commands based on a complete test dataset"""

    @classmethod
    def setUpClass(cls):

        # vtam needs to be in the tsv_path
        subprocess.run([sys.executable, '-m', 'pip', 'install', '{}/.'.format(PathManager.get_package_path()),
                        '--upgrade'])

        cls.package_path = os.path.join(PathManager.get_package_path())
        cls.test_path = os.path.join(PathManager.get_test_path())
        cls.outdir_path = os.path.join(cls.test_path, 'outdir')
        # during development of the test, this prevents errors
        # shutil.rmtree(cls.outdir_path, ignore_errors=True)
        pathlib.Path(cls.outdir_path).mkdir(parents=True, exist_ok=True)
        os.environ['VTAM_LOG_VERBOSITY'] = str(10)

        ############################################################################################
        #
        # Download fastq test dataset
        #
        ############################################################################################

        sorted_tar_path = os.path.join(cls.outdir_path, "sorted.tar.gz")
        if not os.path.isfile(sorted_tar_path):
            urllib.request.urlretrieve(sorted_dryad_f40v5_tar_gz_url, sorted_tar_path)
        tar = tarfile.open(sorted_tar_path, "r:gz")
        tar.extractall(path=cls.outdir_path)
        tar.close()

        cls.args = {}
        cls.args['params'] = os.path.join(os.path.dirname(__file__), "params_lfn_variant.yml")

        ############################################################################################
        #
        # Run 'vtam taxonomy'
        #
        ############################################################################################

        command = "vtam taxonomy --output taxonomy.tsv --precomputed"
        subprocess.run(shlex.split(command), check=True, cwd=cls.outdir_path)

        ############################################################################################
        #
        # Run 'vtam coi_blast_db'
        #
        ############################################################################################

        command = "vtam coi_blast_db --coi_blast_db_dir coi_blast_db_dir"
        subprocess.run(shlex.split(command), check=True, cwd=cls.outdir_path)

    def test_01_filter(self):

        ################################################################################################################
        #
        # Command Filter
        #
        ################################################################################################################

        cmd = "vtam filter --db db.sqlite --readinfo sorted/readinfo.tsv --readdir sorted --asvtable asvtable_default.tsv --params {params}".format(**self.args)
        subprocess.run(shlex.split(cmd), cwd=self.outdir_path)

        asvtable_path = os.path.join(self.outdir_path, "asvtable_default.tsv")
        asvtable_bak_path = os.path.join(self.test_path, "test_files_dryad.f40v5/asvtable_default.tsv")
        self.assertTrue(filecmp.cmp(asvtable_path, asvtable_bak_path, shallow=False))

    def test_02_taxasign(self):

        ################################################################################################################
        #
        # Command Filter
        #
        ################################################################################################################

        command = "vtam taxassign --variants asvtable_default.tsv --output asvtable_default_taxa.tsv --db db.sqlite --blastdbdir coi_blast_db_dir --blastdbname coi_blast_db --taxonomy taxonomy.tsv"
        subprocess.run(shlex.split(command), cwd=self.outdir_path, check=True)

        asvtable_path = os.path.join(self.outdir_path, "asvtable_default_taxa.tsv")
        asvtable_bak_path = os.path.join(self.test_path, "test_files_dryad.f40v5/asvtable_default_taxa.tsv")
        self.assertTrue(filecmp.cmp(asvtable_path, asvtable_bak_path, shallow=False))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.outdir_path, ignore_errors=True)
