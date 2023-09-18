#!/usr/bin/env python


# No need to support Python 2.x anymore.
import configparser
import errno
import json
import os
import re
import sys
from logging import debug

import click
from github import Github, GithubException

try:
    from .version import __version__
except ImportError:  # pragma: no cover
    __version__ = None

DEFAULT_FILENAME = os.path.join("/etc", "github-ssh", "conf")
DEFAULT_CONFIG = """
[env]
"""

# Populate this section with environment variables
for key in os.environ.keys():
    DEFAULT_CONFIG += key + " = " + os.environ[key] + "\n"

DEFAULT_CONFIG += """
[global]
cache_file = /etc/github-ssh/cache.json
access_token =
organization =
teams_default =
users_default =

[users]

[teams]
"""

# Below is the default template for the configuration file.
TPL_CONFIG_FILE = """
# Comments should start with a # and must be full lines
[global]
# The following two lines are mandatory
access_token = <token>
organization = <org>

# In case of connectivity lost and to prevent too many connections to GitHub API,
# it is strongly recommended to set a cache file name.
#
# It must be an absolute filepath.
# By default (when not present) it is set to /etc/github-ssh/cache.json and equivalent to:
# cache_file = /etc/github-ssh/cache.json

# If you want to disable (probably for good reasons), set it to 'false'
# cache_file = [/path/to/file | false]

# Unless overridden after, all users will have these configurations applied.
# By default, nothing is set so basically no one will be granted access
# The '<' case means that if a local exists with the same name as a GitHub user,
# it will be granted access. It is a shorthand to avoid a too
# complex, verbose yet common use case where every developer would
# like to have his/her own shell account.
teams_default = [ list,of,local,users,or,< ]
users_default = [ list,of,local,users,or,< ]

# Configuration below will override team defaults
[teams]
<team_name> = [ list,of,local,users,or,< ]

# And below to override default users setup
[users]
<user_name> = [ list,of,local,users,or,< ]
"""


def do_update(cache_file, access_token, organization):
    retCode = 1
    if len(cache_file) > 0:
        if cache_file != "false":
            if len(access_token) == 0 or len(organization) == 0:
                click.secho(
                    "FATAL: No credential set up to allow GitHub SSH Authentication to work.",
                    fg="red",
                )
                click.secho("Run 'github_ssh_auth init' first.", fg="yellow", bold=True)
            else:
                (userCount, teamCount) = saveCache(cache_file, getKeysFromGitHub(access_token, organization))
                click.secho(
                    "Saved {} users and {} teams for organization '{}' !".format(userCount, teamCount, organization)
                )
                retCode = 0
        else:
            click.secho(
                "Configuration file tells to not use cache, so nothing to be done.",
                fg="yellow",
            )
    else:
        click.secho(
            "cache_file option in configuration file cannot be empty. Please refer to documentation.",
            fg="red",
        )

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
    return re.split(";|,", input)


def getUsersFromLogin(config, cache, login):
    eligibleUsers = set()

    teamsConfig = {key: make_list_of(value) for key, value in config.items("teams")}
    usersConfig = {key: make_list_of(value) for key, value in config.items("users")}

    teamsList = cache["teams"].keys()
    usersList = cache["users"].keys()

    defaultTeamAllowLocalUsers = make_list_of(config.get("global", "teams_default"))
    defaultUserAllowLocalUsers = make_list_of(config.get("global", "users_default"))

    if login in usersList:
        debug(login + " in " + str(usersList))
        debug("got usersConfig: " + str(usersConfig))
        debug("got defaultUserAllowLocalUsers:" + str(defaultUserAllowLocalUsers))
        debug("got teamsConfig: " + str(teamsConfig))
        debug("got defaultTeamAllowLocalUsers:" + str(defaultTeamAllowLocalUsers))
        if login in usersConfig:
            debug("login: " + login + " has " + str(usersConfig[login]))
            if ("<" or login) in usersConfig[login]:
                eligibleUsers.add(login)
                debug("Case 1: add " + login + " to eligibleUsers: " + str(eligibleUsers))
        elif ("<" or login) in defaultUserAllowLocalUsers:
            eligibleUsers.add(login)
            debug("Case 2: add " + login + " to eligibleUsers: " + str(eligibleUsers))

        for team, members in cache["teams"].items():
            debug("looking in team " + team + " got config: " + str(teamsConfig))
            if login in members:
                debug("found login " + login + " in " + str(members))
                if team in teamsConfig:
                    if ("<" or login) in teamsConfig[team]:
                        eligibleUsers.add(login)
                        debug("Case 3: add " + login + " to eligibleUsers: " + str(eligibleUsers))
                elif ("<" or login) in defaultTeamAllowLocalUsers:
                    eligibleUsers.add(login)
                    debug("Case 4: add " + login + " to eligibleUsers: " + str(eligibleUsers))
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
            members = cache["teams"][team]
            eligibleUsers |= set(members)

    return eligibleUsers


def getKeysFromGitHub(access_token, organization):
    UsersCache = {"teams": {}, "users": {}}
    try:
        # First create a Github instance using an access token
        g = Github(access_token)

        # Then focus on organization
        org = g.get_organization(organization)
        for t in org.get_teams():
            for m in t.get_members():
                UsersCache["teams"].setdefault(t.name, []).append(m.login)

        for m in org.get_members():
            UsersCache["users"].setdefault(m.login, [])
            for key in m.get_keys():
                UsersCache["users"][m.login].append(key.key)
    except GithubException as exc:
        click.secho(
            "FATAL: Something went wrong when retrieving data from GitHub. (status = {}, data = {})".format(
                exc.status, exc.data
            ),
            fg="red",
            bold=True,
        )
        sys.exit(1)

    return UsersCache


def saveCache(cache_file, cache):
    try:
        os.makedirs(os.path.dirname(cache_file))
    except OSError as exc:  # pragma: no cover
        if exc.errno != errno.EEXIST:
            click.secho(
                "FATAL: Could not create '{}' (errno={}).".format(cache_file, exc.errno),
                fg="red",
            )
            sys.exit(1)

    with open(cache_file, "w") as fcache:
        try:
            json.dump(cache, fcache)
        except OSError as exc:  # pragma: no cover
            click.secho(
                "FATAL: could not write file '{}' (errno={}) !".format(cache_file, exc.errno),
                fg="red",
            )
            sys.exit(1)

    return (len(cache["users"].keys()), len(cache["teams"].keys()))


def loadCache(cache_file):
    with open(cache_file) as fcache:
        try:
            return json.load(fcache)
        except json.JSONDecodeError:
            click.secho(
                "FATAL: could not parse JSON file '{}' !".format(cache_file),
                fg="red",
            )
            sys.exit(1)
        except OSError as exc:  # pragma: no cover
            click.secho(
                "FATAL: could not read file '{}' (errno={}) !".format(cache_file, exc.errno),
                fg="red",
            )
            sys.exit(1)


@click.group()
@click.version_option(version=__version__)
def cli():
    pass


@cli.command()
@click.option(
    "-c",
    "--config",
    "configfile",
    default=DEFAULT_FILENAME,
    show_default=True,
    help="Config file to use.",
    type=click.Path(dir_okay=False),
)
def update(configfile):
    """
    Update GitHub SSH Auth cache file (users, teams, keys).
    """
    click.secho("Loading config file %s" % configfile, bold=True)

    try:
        os.makedirs(os.path.dirname(configfile))
    except OSError as exc:  # Guard against race condition
        if exc.errno != errno.EEXIST:
            click.secho(
                "FATAL: configuration file '%s' does not exist !" % configfile,
                fg="red",
            )
            click.secho("Run 'github-ssh-init' first.", fg="yellow", bold=True)
            sys.exit(1)

    config = loadConfig(configfile)

    access_token = config.get("global", "access_token")
    organization = config.get("global", "organization")
    cache_file = config.get("global", "cache_file")

    retCode = do_update(cache_file, access_token, organization)
    sys.exit(retCode)


@cli.command()
@click.option(
    "-c",
    "--config",
    "configfile",
    default=DEFAULT_FILENAME,
    show_default=True,
    help="Config file to use.",
    type=click.Path(dir_okay=False),
)
@click.option(
    "-e",
    "--editor",
    "editor",
    default="vim",
    show_default=True,
    help="Editor to use.",
    type=click.Path(dir_okay=False),
)
def init(configfile, editor):
    """
    Initialize GitHub SSH Authentication configuration file.
    """

    filename = click.format_filename(configfile)

    try:
        os.makedirs(os.path.dirname(filename))
    except OSError as exc:
        if exc.errno == errno.EEXIST:
            click.secho(
                "FATAL: configuration file '%s' already exists !" % filename,
                fg="red",
            )
            sys.exit(1)
        else:
            click.secho(
                "FATAL: cannot create directories for configuration file '%s' !" % filename,
                fg="red",
            )
            sys.exit(1)

    # Create config file with the default contents
    try:
        with click.open_file(filename, "w") as f:
            f.write(TPL_CONFIG_FILE)
            f.flush()

        # In this configuration, with a filename, this always returns None
        # so no need to check the return value
        click.edit(
            require_save=True,
            filename=filename,
            editor=editor,
        )

        click.secho("Configuration file '%s' created successfully." % filename, fg="green")
        sys.exit(0)
    except click.UsageError:  # pragma: no cover
        click.secho("FATAL: cannot edit configuration file '%s' !" % configfile, fg="red")
        sys.exit(1)
    except OSError as exc:  # pragma: no cover
        click.secho(
            "FATAL: cannot write configuration file '{}' (errno={}) !".format(configfile, exc.errno),
            fg="red",
        )
        sys.exit(1)


@cli.command()
@click.argument("login")
@click.option(
    "-c",
    "--config",
    "configfile",
    default=DEFAULT_FILENAME,
    show_default=True,
    help="Config file to use.",
    type=click.Path(dir_okay=False),
)
def auth(configfile, login):
    """Authenticate user."""
    config = loadConfig(configfile)

    access_token = config.get("global", "access_token")
    organization = config.get("global", "organization")
    cache_file = config.get("global", "cache_file")

    if len(cache_file) > 0 and cache_file != "false":
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
        keys.extend(UsersCache["users"][user])

    click.echo("\n".join(keys))
    sys.exit(0)
