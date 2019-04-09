# GitHub-SSH-Auth

[![Build Status](https://travis-ci.com/oorabona/github-ssh-auth.svg?branch=master)](https://travis-ci.com/oorabona/github-ssh-auth)

# About

This project aims to provide a way for `SSHd` to authenticate users on shell boxes using GitHub API v3 SSH keys of users in your organization.

# How it works

***SSH Authentication against GitHub API*** is done using a feature of `OpenSSH`, namely `AuthorizedKeysCommand` and `AuthorizedKeysCommandUser`.

Everytime a user connects, the script will be called with the login as command line parameter.

In detail, the following happens :
1. `sshd` deamon runs `github-ssh-auth` under the user defined by `AuthorizedKeysCommandUser` option.

2. `github-ssh-auth` reads its configuration file (by default `/etc/github-ssh/conf`)

3. according to the configuration file, it looks up the username given by `sshd` and checks if that user is granted permission to connect to this host

4. if yes, it tries to read the cache file (recommended but can be disabled) to find user's keys. If no cache file found or if disabled, then it queries GitHub API to get the keys and creates the cache (if enabled).

5. github-ssh-auth returns a list of eligible ssh public keys to standard output to be processed by `sshd`

The rest is handled by `sshd` itself, i.e. checking validity of that public key and the rest of the connection handling.

# Updating keys and cache use

To avoid flooding GitHub API and consequently being temporarily banned from using their API in case of massive connects, it is recommended to keep the cache enabled and update the keys only few times a day. The periodicity is yours and that is why there is a special `update` command line parameter for that.

Consider the following scenario:
- cache is enabled
- cache file already exists
- a new user has joined the team OR an existing user replaced his/her keys

In such case, the cache file will **NOT** be updated when authentication happens, this is the behavior set by design to separate concerns and prevent connection to the outside world being in the critical path for authentication.

Instead, a locally defined `cron` should either:
- call `github-ssh-update` to update cache
- delete cache file (by default `/etc/github-ssh/cache.json`) which will force recreation when next auth happens

Both will have the same outcome but the former is cleaner than the latter.

All in all, choice is yours :wink:

# Installation

Since this Python module deals with SSH authentication, it should be installed globally, hence:

```
$ sudo pip install github-ssh-auth
```

This will install the following program and its shortcuts in `/usr/local/bin`:

## github-ssh

The real application, handling all options, but for convenience the shortcuts described after can be used.

### Usage

```
Usage: github-ssh [OPTIONS] COMMAND [ARGS]...

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  auth    Authenticate user.
  update  Update GitHub SSH Auth cache file (users, teams, keys).
```

## github-ssh-auth

Responsible for authentication itself, this one is to be called by `sshd` itself.

### Usage

```
Usage: github-ssh-auth [OPTIONS] LOGIN

  Authenticate user.

Options:
  -c, --config TEXT
  --help             Show this message and exit.
```

## github-ssh-update

Responsible for updating cache file, it can be scheduled to run periodicaly to ensure synchronization with updated keys from Github.

### Usage

```
Usage: github-ssh-update [OPTIONS]

  Update GitHub SSH Auth cache file (users, teams, keys).

Options:
  -c, --config TEXT
  --help             Show this message and exit.
```

> Note:
In some distros, `/usr/local/bin` is not eligible for `sshd` daemon because of some obscure group permissions reason. Moving the binaries from `/usr/local/bin` to `/usr/bin` make them work like a charm !

# Configuration

## SSH configuration in `/etc/ssh/sshd_config`

These lines should be somewhere in your `sshd` configuration file. Usually in `/etc/ssh/sshd_config` :

```
AuthorizedKeysCommand /usr/bin/github-ssh-auth %u
AuthorizedKeysCommandUser nobody
```

## GitHub token requirements

Since this application is dealing with some sensitive data (users and their team memberships) within an organization, we will need to create a so-called `Personal access tokens`.

To do that, fire up your GitHub organization dashboard, look for `Settings` then `Developer settings`.

Then click on `Generate new token` and set its permissions to:
> read:org

This is the only requirement so that the API can be queried for users and teams memberships. All users keys are public by default an can be accessed from the outside world without authentication against GitHub API.

See for yourself, go to `https://github.com/<yourhandle>.keys`. :rocket:

## GitHub SSH Auth configuration file

It resides by default in `/etc/github-ssh/conf` but of course you can change it using `-c` flag when calling (see above).

The format is a standard INI style, as per `configparser`.

### Configuration file template

Below is the complete grammar with inline comments:

```ini
[global]
# Comments should start with a # and must be full lines
# The following two lines are mandatory
access_token = <token>
organization = <org>

# In case of connectivity lost and to prevent too many connections to GitHub API,
# it is strongly recommended to set it to an absolute filepath.
# Default (when not present) is set to /etc/github-ssh/cache.json and equivalent to:
# cache_file = /etc/github-ssh/cache.json

# If you want to disable, set it to 'false'
# cache_file = [/path/to/file | false]

# Unless overridden after, users (whether individual or teams) will have these configurations applied.
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
...

# And below to override default users setup
[users]
<user_name> = [ list,of,local,users,or,< ]
...
```

### Special note on the '<'

Just a quick focus on that special caracter, designed to allow a GitHub `user` to connect provided that:

- `user` is the Github handle, being part of the organization, **and**
- `user` exists in the local user base (i.e. it is present when you do a `getent passwd`)

#### Real world example

Let's say Acme Corp. wants all its developers connect with their GitHub accounts. Let's say users `jdoe` `bob` `alice` are such handles. Also these user handles are also the respective handlers in GitHub.

Then with this simple configuration, we allow globally all these users to login with their handles:

```ini
[global]
...other config skipped for brevety...

users_default = <
```

Now if you only want `bob` to connect using login `bob`, the configuration file would look like this one:

```ini
[global]
...other config skipped for brevety...

users_default =

[users]
bob = <
```

### Other real world examples

Some other ready-to-be-deployed-or-almost can be found in the `example` directory.

# Testing

As this is my first Python module, and even my first Python program ever, I tried different methods to handle testing.
Having a lot of shortcomings with some of the tools in the ecosystem (`tox`, etc.) due to complexity and such I decided to give a go to Docker with Python installed and everything is done inside containers, which is *super fast*.

So once you have `git clone`d the repository locally, you can see it for yourself by issuing a:

```
$ make help
clean        - remove all build, test, coverage and Python artifacts
clean-build  - remove build artifacts
clean-pyc    - remove Python file artifacts
clean-test   - remove test and coverage artifacts
lint         - check style with flake8
test         - run tests quickly with the default Python
coverage     - check code coverage quickly with the default Python
docs         - generate Sphinx HTML documentation, including API docs
release      - package and upload a release
test-release - package and upload a release to testpy repository
dist         - package
install      - install the package to the active Python's site-packages
```

# Contributions

Comments, issues, PR as :beer: will be warmly welcomed !

# License

GPLv3+
