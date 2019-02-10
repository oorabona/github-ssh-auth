# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import unittest

from click.testing import CliRunner
from github_ssh_auth.cli import cli
from github import GithubException

class TestCliInit(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()

    # def test_update_non_existing_configfile(self):
    #     with self.runner.isolated_filesystem():
    #         result = self.runner.invoke(cli, ['update', '-c', 'not-exist.cfg'])
    #         assert 'FATAL: configuration file not-exist.cfg empty or invalid !' in result.output
    #         assert result.exit_code == 1
    #
    # def test_update_no_config(self):
    #     result = self.runner.invoke(cli, ['update', '-c', 'test/empty.cfg'])
    #     assert 'FATAL: configuration file test/empty.cfg empty or invalid !' in result.output
    #     assert result.exit_code == 1
    #
    # def test_update_no_cache(self):
    #     result = self.runner.invoke(cli, ['update', '--config', 'test/no_cache_file.cfg'])
    #     assert 'Configuration file tells to not use cache, so nothing to be done.' in result.output
    #     assert result.exit_code == 1
    #
    # def test_update_no_cache_set_empty(self):
    #     result = self.runner.invoke(cli, ['update', '--config', 'test/empty_cache_file.cfg'])
    #     assert 'cache_file cannot be empty. Please refer to documentation.' in result.output
    #     assert result.exit_code == 1
    #
    # def test_update_use_default_cache_file(self):
    #     result = self.runner.invoke(cli, ['update', '-c', 'test/use_default_cache.cfg'])
    #     assert 'Loading config file test/use_default_cache.cfg' in result.output
    #     assert isinstance(result.exception, GithubException)
