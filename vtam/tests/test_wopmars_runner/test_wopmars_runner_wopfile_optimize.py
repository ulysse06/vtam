import os
import shutil
import sys
import unittest
import yaml

from vtam.utils.ArgParser import ArgParser
from vtam.utils.PathManager import PathManager
from vtam.utils.WopmarsRunner import WopmarsRunner


class TestWorpmarsRunnerOptimize(unittest.TestCase):

    def setUp(self):

        self.package_path = PathManager.get_package_path()
        test_path = PathManager.get_test_path()

        # Minimal merge command
        foopaths = {}
        foopaths['foofile'] = os.path.relpath(__file__, self.package_path)
        foopaths['foodir'] = os.path.relpath(
            os.path.dirname(__file__), self.package_path)
        foopaths['outdir'] = os.path.relpath(
            os.path.join(test_path, 'output'), self.package_path)
        foopaths['blastdb'] = os.path.relpath(os.path.join(
            test_path, 'test_files', 'blastdb'), self.package_path)
        foopaths['readinfo_tsv'] = os.path.join("doc", "data", "readinfo_mfzr.tsv")
        foopaths['tsv_path'] = os.path.join("doc", "data", "readinfo_mfzr.tsv")
        foopaths['known_occurrences'] = os.path.join("doc", "data", "known_occurrences.tsv")
        self.foopaths = foopaths

    def test_wopmars_runner_optimize(self):

        cmd = 'optimize --readinfo {readinfo_tsv} --readdir {foodir} --known_occurrences {known_occurrences} --outdir {outdir}'\
            .format(**self.foopaths)

        cwd = os.getcwd()
        os.chdir(self.package_path)
        args = ArgParser.get_main_arg_parser().parse_args(cmd.split(" "))
        os.chdir(cwd)

        wopmars_runner = WopmarsRunner(command='optimize', cli_args_dic=vars(args))
        wopfile_path = os.path.relpath(os.path.join(self.package_path, "tests", "output", "wopfile"), self.package_path)
        wopfile_path, wopfile_content = wopmars_runner.create_wopfile(path=wopfile_path)

        with open(os.path.join(os.path.dirname(__file__), "wopfile_optimize.yml")) as fin:
            wopfile_content_bak = fin.read()
        if not sys.platform.startswith("win"):
            self.assertTrue(wopfile_content == wopfile_content_bak)

    def test_wopmars_runner_optimize_lfn_variant_replicate(self):

        cmd = 'optimize --readinfo {readinfo_tsv} --readdir {foodir} --known_occurrences {known_occurrences} --outdir {outdir} --lfn_variant_replicate'\
            .format(**self.foopaths)

        cwd = os.getcwd()
        os.chdir(self.package_path)
        args = ArgParser.get_main_arg_parser().parse_args(cmd.split(" "))
        os.chdir(cwd)

        wopmars_runner = WopmarsRunner(command='optimize', cli_args_dic=vars(args))
        wopfile_path = os.path.relpath(os.path.join(self.package_path, "tests/output/wopfile"), self.package_path)
        wopfile_path, wopfile_content = wopmars_runner.create_wopfile(path=wopfile_path)

        self.assertFalse('lfn_variant_cutoff' in yaml.load(wopfile_content, Loader=yaml.SafeLoader)['rule OptimizeLFNreadCountAndLFNvariant']['params'])
        self.assertTrue('lfn_variant_replicate_cutoff' in yaml.load(wopfile_content, Loader=yaml.SafeLoader)['rule OptimizeLFNreadCountAndLFNvariant']['params'])

    def tearDown(self):
        shutil.rmtree(self.foopaths['outdir'], ignore_errors=True)
