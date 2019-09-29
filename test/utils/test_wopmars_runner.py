import os
from unittest import TestCase
from wopmetabarcoding.utils.ArgParser import ArgParser

from wopmetabarcoding.utils.OptionManager import OptionManager
from wopmetabarcoding.utils.WopmarsRunner import WopmarsRunner
from wopmetabarcoding.utils.PathManager import PathManager


class TestWorpmarsRunner(TestCase):

    def test_wopmars_runner_merge(self):
        #
        # Minimal merge command
        args_str = 'merge --fastqinfo {} --fastqdir {} --fastainfo foo --fastadir foo'.format(
            os.path.relpath(__file__, PathManager.get_package_path()),
            os.path.relpath(os.path.dirname(__file__), PathManager.get_package_path()))
        parser = ArgParser.get_arg_parser(abspath=False)
        args = parser.parse_args(args_str.split())
        #####################
        #
        # Add argparser attributes to optionmanager
        #
        #####################
        for k in vars(args):
            OptionManager.instance()[k] = vars(args)[k]
        ###############################################################
        #
        # Test wopfile
        #
        ###############################################################
        wopmars_runner = WopmarsRunner(subcommand='merge', parameters=OptionManager.instance())
        # wopfile_path = os.path.relpath(PathManager.get_package_path(), os.path.join(PathManager.get_module_test_path(), "../output/Wopfile.yml"))
        # import pdb; pdb.set_trace()
        wopfile_path = os.path.relpath(os.path.join(PathManager.get_package_path(), "test/output/wopfile"), PathManager.get_package_path())
        wopfile_path, wopfile_content = wopmars_runner.create_wopfile(path=wopfile_path)
        # import pdb; pdb.set_trace()
        wopfile_content_bak = """rule Merge:
  tool: wopmetabarcoding.wrapper.Merge
  input:
      file:
          sample2fastq: test/utils/test_wopmars_runner.py
  output:
      file:
          fastainfo: foo
  params:
      fastq_directory: test/utils
      fasta_dir: foo
      fastq_minovlen: 50
      fastq_maxmergelen: 300
      fastq_minmergelen: 100
      fastq_minlen: 50
      fastq_maxee: 1
      fastq_truncqual: 10
      fastq_maxns: 0
      threads: 8
      fastq_ascii: 33"""
        self.assertTrue(wopfile_content == wopfile_content_bak)
        ###############################################################
        #
        # Test wopmars command
        #
        ###############################################################
        wopmars_command = wopmars_runner.get_wopmars_command()
        wopmars_runner.wopfile_path = "Wopfile_merge"
        self.assertTrue(wopmars_command == 'wopmars merge -w test/output/wopfile -D sqlite:///db.sqlite -p -v '
                                           '--fastainfo foo --fastadir test/utils')

    # def test_wopmars_command_merge(self):
    #     #
    #     # Minimal merge command
    #     args_str = 'merge --fastqinfo {} --fastqdir {} --fastainfo foo --fastadir foo'.format(
    #         os.path.relpath(__file__, PathManager.get_package_path()),
    #         os.path.relpath(os.path.dirname(__file__), PathManager.get_package_path()))
    #     parser = ArgParser.get_arg_parser(abspath=False)
    #     args = parser.parse_args(args_str.split())
    #     #####################
    #     #
    #     # Add argparser attributes to optionmanager
    #     #
    #     #####################
    #     for k in vars(args):
    #         print(k,vars(args)[k])
    #         OptionManager.instance()[k] = vars(args)[k]
    #     #####################
    #     #
    #     # Test wopfile
    #     #
    #     #####################
    #     wopmars_runner = WopmarsRunner(subcommand='merge', parameters=OptionManager.instance())
    #     wopmars_runner.wopfile_path = "Wopfile_merge"
    #
    #     #####################
    #     #
    #     # Test wopmars command
    #     #
    #     #####################
    #     wopmars_command = wopmars_runner.get_wopmars_command()
    #     self.assertTrue(wopmars_command == 'wopmars merge -w Wopfile_merge -D sqlite:///db.sqlite -p -v --fastainfo foo '
    #                                        '--fastadir test/utils')


