import codecs
import os
import textwrap

# from setuptools import setup

gh_ref_name = os.getenv("GITHUB_REF_NAME")
version_py = textwrap.dedent(
    f"""
    # coding: utf-8
    from __future__ import unicode_literals
    __version__ = {gh_ref_name}
    """
)

print("Setting version file to '{}'".format(gh_ref_name))
with codecs.open("github_ssh_auth/version.py", "a", "utf-8") as file_handler:
    file_handler.write(version_py)
