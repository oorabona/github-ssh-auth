# -*- coding: utf8 -*-
# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import unittest
import os
import errno
import json
import warnings
import six

from click.testing import CliRunner
from github_ssh_auth.cli import cli

DEFAULT_CONFIGFILE = os.path.join('etc', 'github_ssh_auth', 'conf')
DEFAULT_CACHEFILE = 'etc/github_ssh_auth/test.json'

TEST_CONFIG = """
[global]
access_token =
organization =
cache_file = {cache_file}
teams_default = app,<
users_default = app,<
[teams]
team1 = <
team2 = admin
[users]
user4 = admin
user5 = <
""".format(cache_file=DEFAULT_CACHEFILE)

TEST_CACHE = {
    'users': {
        'user1': ['key_user_1'],
        'user2': ['key_user_2'],
        'user3': ['key_user_3'],
        'user4': ['key_user_4'],
        'user5': ['key_user_5'],
        'user6': ['key_user_6']
    },
    'teams': {
        'team1': ['user1'],
        'team2': ['user1', 'user2'],
        'team3': ['user2', 'user3']
    }
}

TPL_TEST_CONFIG = """
[global]
cache_file = {cache_file}
"""

def countOutputKeys(output):
    return len(output.split('\n')) - 1

class TestCliAuthUser(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()
        #  In python3, the urllib3 library may raise these socket resource
        #  warnings. They should be benign and an artifact of a performance
        #  optimization of reusing the sockets.
        #  https://github.com/mementoweb/py-memento-client/issues/6#issuecomment-196381413
        if six.PY3:
            warnings.filterwarnings(
                "ignore",
                message="unclosed <ssl.SSLSocket",
                category=ResourceWarning)

    def test_auth_team_user1(self):
        with self.runner.isolated_filesystem():
            try:
                os.makedirs(os.path.dirname(DEFAULT_CONFIGFILE))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
            with open(DEFAULT_CONFIGFILE, 'w') as f:
                f.write(TEST_CONFIG)
            with open(DEFAULT_CACHEFILE, 'w') as f:
                json.dump(TEST_CACHE, f)

            result = self.runner.invoke(cli, ['auth', 'user1', '-c', DEFAULT_CONFIGFILE])
            assert countOutputKeys(result.output) == 1
            assert 'key_user_1' in result.output
            assert result.exit_code == 0

    def test_auth_team_user2(self):
        with self.runner.isolated_filesystem():
            try:
                os.makedirs(os.path.dirname(DEFAULT_CONFIGFILE))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
            with open(DEFAULT_CONFIGFILE, 'w') as f:
                f.write(TEST_CONFIG)
            with open(DEFAULT_CACHEFILE, 'w') as f:
                json.dump(TEST_CACHE, f)

            result = self.runner.invoke(cli, ['auth', 'user2', '-c', DEFAULT_CONFIGFILE])
            assert countOutputKeys(result.output) == 1
            assert 'key_user_2' in result.output
            assert result.exit_code == 0

    def test_auth_team_user3(self):
        with self.runner.isolated_filesystem():
            try:
                os.makedirs(os.path.dirname(DEFAULT_CONFIGFILE))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
            with open(DEFAULT_CONFIGFILE, 'w') as f:
                f.write(TEST_CONFIG)
            with open(DEFAULT_CACHEFILE, 'w') as f:
                json.dump(TEST_CACHE, f)

            result = self.runner.invoke(cli, ['auth', 'user3', '-c', DEFAULT_CONFIGFILE])
            assert countOutputKeys(result.output) == 1
            assert 'key_user_3' in result.output
            assert result.exit_code == 0

    def test_auth_team_user4(self):
        with self.runner.isolated_filesystem():
            try:
                os.makedirs(os.path.dirname(DEFAULT_CONFIGFILE))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
            with open(DEFAULT_CONFIGFILE, 'w') as f:
                f.write(TEST_CONFIG)
            with open(DEFAULT_CACHEFILE, 'w') as f:
                json.dump(TEST_CACHE, f)

            result = self.runner.invoke(cli, ['auth', 'user4', '-c', DEFAULT_CONFIGFILE])
            assert len(result.output) == 1
            assert result.exit_code == 0

    def test_auth_team_user5(self):
        with self.runner.isolated_filesystem():
            try:
                os.makedirs(os.path.dirname(DEFAULT_CONFIGFILE))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
            with open(DEFAULT_CONFIGFILE, 'w') as f:
                f.write(TEST_CONFIG)
            with open(DEFAULT_CACHEFILE, 'w') as f:
                json.dump(TEST_CACHE, f)

            result = self.runner.invoke(cli, ['auth', 'user5', '-c', DEFAULT_CONFIGFILE])
            assert countOutputKeys(result.output) == 1
            assert 'key_user_5' in result.output
            assert result.exit_code == 0

    def test_auth_team_app(self):
        with self.runner.isolated_filesystem():
            try:
                os.makedirs(os.path.dirname(DEFAULT_CONFIGFILE))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
            with open(DEFAULT_CONFIGFILE, 'w') as f:
                f.write(TEST_CONFIG)
            with open(DEFAULT_CACHEFILE, 'w') as f:
                json.dump(TEST_CACHE, f)

            result = self.runner.invoke(cli, ['auth', 'app', '-c', DEFAULT_CONFIGFILE])
            assert countOutputKeys(result.output) == 4
            assert ('key_user_1' and 'key_user_2' and 'key_user_3' and 'key_user_6') in result.output
            assert result.exit_code == 0

    def test_auth_team_admin(self):
        with self.runner.isolated_filesystem():
            try:
                os.makedirs(os.path.dirname(DEFAULT_CONFIGFILE))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
            with open(DEFAULT_CONFIGFILE, 'w') as f:
                f.write(TEST_CONFIG)
            with open(DEFAULT_CACHEFILE, 'w') as f:
                json.dump(TEST_CACHE, f)

            result = self.runner.invoke(cli, ['auth', 'admin', '-c', DEFAULT_CONFIGFILE])
            assert countOutputKeys(result.output) == 3
            assert ('key_user_1' and 'key_user_2' and 'key_user_4') in result.output
            assert result.exit_code == 0

    def test_auth_real_user_with_cache(self):
        with self.runner.isolated_filesystem():
            try:
                os.makedirs(os.path.dirname(DEFAULT_CONFIGFILE))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
            with open(DEFAULT_CONFIGFILE, 'w') as f:
                TEST_CONFIG = TPL_TEST_CONFIG.format(cache_file=DEFAULT_CACHEFILE)
                TEST_CONFIG += "access_token = ${env:ACCESS_TOKEN}\n"
                TEST_CONFIG += "organization = ${env:GITHUB_ORG}\n"
                TEST_CONFIG += "users_default = <"
                f.write(TEST_CONFIG)

            result = self.runner.invoke(cli, ['auth', 'oorabona', '-c', DEFAULT_CONFIGFILE])
            # print('Test config: ' + TEST_CONFIG)
            # print('Result: ' + result.output + '\nLen: '+str(countOutputKeys(result.output)))
            assert countOutputKeys(result.output) > 1
            assert result.exit_code == 0

    def test_auth_real_user_without_cache(self):
        with self.runner.isolated_filesystem():
            try:
                os.makedirs(os.path.dirname(DEFAULT_CONFIGFILE))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
            with open(DEFAULT_CONFIGFILE, 'w') as f:
                TEST_CONFIG = TPL_TEST_CONFIG.format(cache_file='false')
                TEST_CONFIG += "access_token = ${env:ACCESS_TOKEN}\n"
                TEST_CONFIG += "organization = ${env:GITHUB_ORG}\n"
                TEST_CONFIG += "users_default = <"
                f.write(TEST_CONFIG)

            result = self.runner.invoke(cli, ['auth', 'oorabona', '-c', DEFAULT_CONFIGFILE])
            assert countOutputKeys(result.output) > 1
            assert result.exit_code == 0

    def test_noauth_existing_user(self):
        with self.runner.isolated_filesystem():
            try:
                os.makedirs(os.path.dirname(DEFAULT_CONFIGFILE))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
            with open(DEFAULT_CONFIGFILE, 'w') as f:
                TEST_CONFIG = TPL_TEST_CONFIG.format(cache_file=DEFAULT_CACHEFILE)
                TEST_CONFIG += "access_token = ${env:ACCESS_TOKEN}\n"
                TEST_CONFIG += "organization = ${env:GITHUB_ORG}\n"
                f.write(TEST_CONFIG)

            result = self.runner.invoke(cli, ['auth', 'oorabona', '-c', DEFAULT_CONFIGFILE])
            assert len(result.output) == 1
            assert result.exit_code == 0

    def test_noauth_nonexisting_user(self):
        with self.runner.isolated_filesystem():
            try:
                os.makedirs(os.path.dirname(DEFAULT_CONFIGFILE))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
            with open(DEFAULT_CONFIGFILE, 'w') as f:
                TEST_CONFIG = TPL_TEST_CONFIG.format(cache_file=DEFAULT_CACHEFILE)
                TEST_CONFIG += "access_token = ${env:ACCESS_TOKEN}\n"
                TEST_CONFIG += "organization = ${env:GITHUB_ORG}\n"
                TEST_CONFIG += "users_default = <"
                f.write(TEST_CONFIG)

            result = self.runner.invoke(cli, ['auth', 'nobody', '-c', DEFAULT_CONFIGFILE])
            assert len(result.output) == 1
            assert result.exit_code == 0
