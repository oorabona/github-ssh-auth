# -*- coding: utf-8 -*-
# This file is part of 'miniver': https://github.com/jbweston/miniver
#
# The default value "__use_git__" is replaced by the actual version number
# during the build process.

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

    # Actually retrieving the latest version from PyPI is a bit of a pain.
    # We cannot fully rely on info.version for the latest version, because
    # it seems to be only the "base" version, not the "full" (i.e. public) version.
    # So we have to do some extra work to get the latest version from the 'releases' instead.
    # latest_version_str = r.json()["info"]["version"]
    latest_version_str = [k for k in r.json()["releases"].keys()][-1]

    is_ci = os.getenv("CI", False)

    # Set local version when we have a branch (ref_name is not a tag)
    if is_ci:
        # Get N in devN version string
        latest_version = parse(latest_version_str)
        dev = latest_version.dev
        # Increment dev version
        if dev is not None:
            dev = int(dev) + 1
        else:
            dev = 0
        return Version(f"{latest_version.base_version}.dev", dev, "")
    return Version("0.0.0.dev", 0, None)


# These values are only set if the distribution was created with 'git archive'
refnames = "$Format:%D$"
git_hash = "$Format:%h$"
