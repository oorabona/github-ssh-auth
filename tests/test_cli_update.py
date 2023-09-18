# Make coding more python3-ish


import errno
import os
import unittest

from click.testing import CliRunner

from github_ssh_auth.cli import cli

DEFAULT_CONFIGFILE = os.path.join("etc", "github_ssh_auth", "conf")
DEFAULT_CACHEFILE = "etc/github_ssh_auth/test.json"

TEST_CONFIG = """
[global]
cache_file = {cache_file}
""".format(
    cache_file=DEFAULT_CACHEFILE
)

TEST_CONFIG += "access_token = " + os.environ.get("ACCESS_TOKEN") + "\n"
TEST_CONFIG += "organization = " + os.environ.get("GITHUB_ORG") + "\n"


class TestCliUpdate(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_update_non_existing_configfile(self):
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(cli, ["update", "-c", "not-exist.cfg"])
            assert "FATAL: configuration file 'not-exist.cfg' does not exist !" in result.output
            assert result.exit_code == 1

    def test_update_no_config(self):
        result = self.runner.invoke(cli, ["update", "-c", "tests/empty.cfg"])
        assert "FATAL: No credential set up to allow GitHub SSH Authentication to work." in result.output
        assert result.exit_code == 1

    def test_update_no_cache(self):
        result = self.runner.invoke(cli, ["update", "--config", "tests/no_cache_file.cfg"])
        assert "Configuration file tells to not use cache, so nothing to be done." in result.output
        assert result.exit_code == 1

    def test_update_no_cache_set_empty(self):
        result = self.runner.invoke(cli, ["update", "--config", "tests/empty_cache_file.cfg"])
        assert (
            "cache_file option in configuration file cannot be empty. Please refer to documentation." in result.output
        )
        assert result.exit_code == 1

    def test_update_use_default_cache_file(self):
        result = self.runner.invoke(cli, ["update", "-c", "tests/use_default_cache.cfg"])
        assert "FATAL: No credential set up to allow GitHub SSH Authentication to work." in result.output
        assert result.exit_code == 1

    def test_update_bad_credentials(self):
        result = self.runner.invoke(cli, ["update", "-c", "tests/bad_credentials.cfg"])
        assert "FATAL: Something went wrong when retrieving data from GitHub." in result.output
        assert result.exit_code == 1

    def test_update_good_credentials(self):
        with self.runner.isolated_filesystem():
            try:
                os.makedirs(os.path.dirname(DEFAULT_CONFIGFILE))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
            with open(DEFAULT_CONFIGFILE, "w") as f:
                f.write(TEST_CONFIG)

            result = self.runner.invoke(cli, ["update", "-c", DEFAULT_CONFIGFILE])
            # print("RESULT: "+result.output)
            assert f"Loading config file etc{os.sep}github_ssh_auth{os.sep}conf" in result.output
            assert "Saved" in result.output
            assert result.exit_code == 0

            assert os.path.getsize(DEFAULT_CACHEFILE) > 0
