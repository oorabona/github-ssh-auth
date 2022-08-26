# -*- coding: utf-8 -*-
# This file is part of 'miniver': https://github.com/jbweston/miniver
#
# This file will be overwritten by setup.py when a source or binary
# distribution is made.  The magic value "__use_git__" is interpreted by
# _version.py.

import os
from collections import namedtuple

Version = namedtuple("Version", ("release", "dev", "labels"))

ref_name = os.getenv("GITHUB_REF_NAME")

version = "__use_git__"
# default_version = "0.0.0"


def default_version():
    global ref_name
    global Version
    if ref_name is not None and ref_name != "":
        return Version("0.0.0.dev", 0, [ref_name])
    return Version("0.0.0.dev", 0, None)


# These values are only set if the distribution was created with 'git archive'
refnames = "$Format:%D$"
git_hash = "$Format:%h$"
