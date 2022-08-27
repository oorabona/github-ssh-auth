# -*- coding: utf-8 -*-
# This file is part of 'miniver': https://github.com/jbweston/miniver
#
# This file will be overwritten by setup.py when a source or binary
# distribution is made.  The magic value "__use_git__" is interpreted by
# _version.py.

version = "__use_git__"
# default_version = "0.0.0"


def default_version():
    import os
    from collections import namedtuple

    import requests
    from packaging.version import parse

    Version = namedtuple("Version", ("release", "dev", "labels"))

    r = requests.get("https://test.pypi.org/pypi/github-ssh-auth/json")
    r.raise_for_status()

    latest_version_str = r.json()["info"]["version"]

    is_ci = os.getenv("CI_RUN")

    # Set local version when we have a branch (ref_name is not a tag)
    if is_ci:
        # Get N in devN version string
        latest_version = parse(latest_version_str)
        dev = latest_version.dev
        # Increment dev version
        if dev:
            dev = int(dev) + 1
        else:
            dev = 0
        return Version(f"{latest_version.public}.dev", dev, "")
    return Version("0.0.0.dev", 0, None)


# These values are only set if the distribution was created with 'git archive'
refnames = "$Format:%D$"
git_hash = "$Format:%h$"
