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
    import re
    from collections import namedtuple

    import requests
    from packaging import version

    r = requests.get("https://test.pypi.org/pypi/github-ssh-auth/json")
    r.raise_for_status()

    latest_version = r.json()["info"]["version"]

    Version = namedtuple("Version", ("release", "dev", "labels"))

    is_ci = os.getenv("CI")

    # Set local version when we have a branch (ref_name is not a tag)
    if is_ci:
        # Get N in devN version string
        result = re.search(version.VERSION_PATTERN, latest_version)
        dev = result.group("dev") if result else None
        # Increment dev version
        if dev:
            dev = int(dev) + 1
        else:
            dev = 0
        return Version("0.0.0.dev", dev, "")
    return Version("0.0.0.dev", 0, None)


# These values are only set if the distribution was created with 'git archive'
refnames = "$Format:%D$"
git_hash = "$Format:%h$"
