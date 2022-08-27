# Make coding more python3-ish
from __future__ import absolute_import, division, print_function

__metaclass__ = type

import unittest

from click.testing import CliRunner
from github import GithubException

from github_ssh_auth.cli import cli


class TestCliInit(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_init_no_args(self):
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(cli, ["init"])
            self.assertEqual(result.exit_code, 1)
            self.assertIn("FATAL: cannot create directories for configuration file '/etc/github-ssh/conf' !", result.output)

    def test_init_with_args(self):
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(cli, ["init", "--config", "tests/new.cfg", "-e", "cat"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Configuration file 'tests/new.cfg' created successfully.", result.output)

    def test_init_with_existing_config(self):
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(cli, ["init", "--config", "tests/new.cfg", "-e", "cat"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Configuration file 'tests/new.cfg' created successfully.", result.output)
            result = self.runner.invoke(cli, ["init", "--config", "tests/new.cfg", "-e", "cat"])
            self.assertEqual(result.exit_code, 1)
            self.assertIn("configuration file 'tests/new.cfg' already exists", result.output)