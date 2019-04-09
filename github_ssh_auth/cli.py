#!/usr/bin/env python
# -*- coding: utf8 -*-
from __future__ import absolute_import, division, print_function
__metaclass__ = type

import os
import sys
import json
import errno
import re

from logging import debug, warning, error

import click
try:
    import configparser
except ImportError:
    import ConfigParser

from github import Github, GithubException

DEFAULT_FILENAME = os.path.join('/etc', 'github-ssh', 'conf')
DEFAULT_CONFIG = u"""
[env]
"""

# Populate this section with environment variables
for key in os.environ.keys():
    DEFAULT_CONFIG += key + " = " + os.environ[key] + '\n'

# Then add default parameters
DEFAULT_CONFIG += u"""
[global]
cache_file = /etc/github-ssh/cache.json
access_token =
organization =

teams_default =
users_default =

[teams]

[users]
"""

MARKER = u"""
# Below are default values, please do not edit after this line as it will be ignored.
# If you want to change them, please do it above.
"""


def do_update(cache_file, access_token, organization):
    retCode = 1
    if len(cache_file) > 0:
        if cache_file != 'false':
            if len(access_token) == 0 or len(organization) == 0:
                click.secho("FATAL: No credential set up to allow GitHub SSH Authication to work.", fg='red')
                click.secho("Run 'github_ssh_auth init' first.", fg='yellow', bold=True)
            else:
                (userCount, teamCount) = saveCache(cache_file, getKeysFromGitHub(access_token, organization))
                click.secho("Saved %s users and %s teams for organization '%s' !" % (userCount, teamCount, organization))
                retCode = 0
        else:
            click.secho("Configuration file tells to not use cache, so nothing to be done.", fg='yellow')
    else:
        click.secho("cache_file option in configuration file cannot be empty. Please refer to documentation.", fg='red')

    return retCode


def loadConfig(configfile):
    config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation(), allow_no_value=True)
    config.optionxform = str
    config.read_string(DEFAULT_CONFIG)
    config.read(configfile)
    return config


def make_list_of(input):
    # configparse will eventually have values as string.
    # so we can split in tokens using a separator found automagically :)
    return re.split(';|,', input)


def getUsersFromLogin(config, cache, login):
    eligibleUsers = set()

    teamsConfig = dict((key, make_list_of(value)) for key, value in config.items('teams'))
    usersConfig = dict((key, make_list_of(value)) for key, value in config.items('users'))

    teamsList = cache['teams'].keys()
    usersList = cache['users'].keys()

    defaultTeamAllowLocalUsers = make_list_of(config.get('global', 'teams_default'))
    defaultUserAllowLocalUsers = make_list_of(config.get('global', 'users_default'))

    if login in usersList:
        debug(login + ' in ' + str(usersList))
        debug('got usersConfig: ' + str(usersConfig))
        debug('got defaultUserAllowLocalUsers:' + str(defaultUserAllowLocalUsers))
        debug('got teamsConfig: ' + str(teamsConfig))
        debug('got defaultTeamAllowLocalUsers:' + str(defaultTeamAllowLocalUsers))
        if login in usersConfig:
            debug('login: ' + login + ' has ' + str(usersConfig[login]))
            if ('<' or login) in usersConfig[login]:
                eligibleUsers.add(login)
                debug('Case 1: add ' + login + ' to eligibleUsers: ' + str(eligibleUsers))
        elif ('<' or login) in defaultUserAllowLocalUsers:
            eligibleUsers.add(login)
            debug('Case 2: add ' + login + ' to eligibleUsers: ' + str(eligibleUsers))

        for team, members in cache['teams'].items():
            debug('looking in team ' + team + ' got config: ' + str(teamsConfig))
            if login in members:
                debug('found login ' + login + ' in ' + str(members))
                if team in teamsConfig:
                    if ('<' or login) in teamsConfig[team]:
                        eligibleUsers.add(login)
                        debug('Case 3: add ' + login + ' to eligibleUsers: ' + str(eligibleUsers))
                elif ('<' or login) in defaultTeamAllowLocalUsers:
                    eligibleUsers.add(login)
                    debug('Case 4: add ' + login + ' to eligibleUsers: ' + str(eligibleUsers))
    else:
        for user in usersList:
            if user in usersConfig:
                if login in usersConfig[user]:
                    eligibleUsers.add(user)
            elif login in defaultUserAllowLocalUsers:
                eligibleUsers.add(user)

        eligibleTeams = set()
        for team in teamsList:
            if team in teamsConfig:
                if login in teamsConfig[team]:
                    eligibleTeams.add(team)
            elif login in defaultTeamAllowLocalUsers:
                eligibleTeams.add(team)

        for team in eligibleTeams:
            members = cache['teams'][team]
            eligibleUsers |= set(members)

    return eligibleUsers


def getKeysFromGitHub(access_token, organization):
    UsersCache = {'teams': {}, 'users': {}}
    try:
        # First create a Github instance using an access token
        g = Github(access_token)

        # Then focus on organization
        org = g.get_organization(organization)
        for t in org.get_teams():
            for m in t.get_members():
                UsersCache['teams'].setdefault(t.name, []).append(m.login)

        for m in org.get_members():
            UsersCache['users'].setdefault(m.login, [])
            for key in m.get_keys():
                UsersCache['users'][m.login].append(key.key)
    except GithubException as exc:
        click.secho("FATAL: Something went wrong when retrieving data from GitHub. (status = %s, data = %s)" % (exc.status, exc.data), fg='red', bold=True)
        sys.exit(1)

    return UsersCache


def saveCache(cache_file, cache):
    try:
        os.makedirs(os.path.dirname(cache_file))
    except OSError as exc:  # Guard against race condition
        if exc.errno != errno.EEXIST:   # pragma: no cover
            click.secho("FATAL: Could not create '%s' (errno=%s)." % (cache_file, exc.errno), fg='red')
            sys.exit(1)

    with open(cache_file, 'w') as fcache:
        json.dump(cache, fcache)

    return (len(cache['users'].keys()), len(cache['teams'].keys()))


def loadCache(cache_file):
    with open(cache_file, 'r') as fcache:
        return json.load(fcache)


@click.group()
@click.version_option()
def cli():
    pass


@cli.command()
@click.option('-c', '--config', 'configfile', default=DEFAULT_FILENAME)
def update(configfile):
    """
    Update GitHub SSH Auth cache file (users, teams, keys).
    """
    click.secho('Loading config file %s' % configfile, bold=True)

    try:
        os.makedirs(os.path.dirname(configfile))
    except OSError as exc:  # Guard against race condition
        if exc.errno != errno.EEXIST:
            click.secho("FATAL: configuration file '%s' does not exist !" % configfile, fg='red')
            click.secho("Run 'github_ssh_auth init' first.", fg='yellow', bold=True)
            sys.exit(1)

    config = loadConfig(configfile)

    access_token = config.get('global', 'access_token')
    organization = config.get('global', 'organization')
    cache_file = config.get('global', 'cache_file')

    retCode = do_update(cache_file, access_token, organization)
    sys.exit(retCode)


# @cli.command()
# @click.option('-c', '--config', 'configfile', default=DEFAULT_FILENAME)
# def init(configfile):
#     """
#     Initialize GitHub SSH Authentication configuration file.
#     """
#
#     message = click.edit('\n' + MARKER + DEFAULT_CONFIG)
#     if message is not None:
#         click.secho(message.split(MARKER, 1)[0].rstrip('\n'))
#
#     click.secho('Wrote GitHub SSH Authentication configuration file : %s' % configfile, bold=True)
#     sys.exit(0)


@cli.command()
@click.argument('login')
@click.option('-c', '--config', 'configfile', default=DEFAULT_FILENAME)
def auth(configfile, login):
    """Authenticate user."""
    config = loadConfig(configfile)

    access_token = config.get('global', 'access_token')
    organization = config.get('global', 'organization')
    cache_file = config.get('global', 'cache_file')

    if len(cache_file) > 0 and cache_file != 'false':
        if os.path.isfile(cache_file):
            UsersCache = loadCache(cache_file)
        else:
            UsersCache = getKeysFromGitHub(access_token, organization)
            saveCache(cache_file, UsersCache)
    else:
        UsersCache = getKeysFromGitHub(access_token, organization)

    # Get eligible users...
    eligibleUsers = getUsersFromLogin(config, UsersCache, login)

    keys = []
    for user in eligibleUsers:
        keys.extend(UsersCache['users'][user])

    click.echo('\n'.join(keys))
    sys.exit(0)
