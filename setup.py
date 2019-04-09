# -*- coding: utf-8 -*-

"""Use your GitHub organization user's keys as a SSH authentication method."""

from __future__ import absolute_import, division, print_function

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup_requires = []

install_requires = [
    'click>=7.0',
    'PyGithub>=1.2.0',
    'configparser'
]

docs_require = []

tests_require = [
    'flake8',
    'pytest',
    'pytest-cov',
    'coverage',
]

extras_require = {
    'docs': docs_require,
    'tests': tests_require,
}

extras_require['all'] = []
for name, reqs in extras_require.items():
    if name not in ['all']:
        extras_require['all'].extend(reqs)

packages = find_packages(exclude=['docs', 'tests'])
url = "https://github.com/oorabona/github-ssh-auth"

setup(
    name="github-ssh-auth",
    autosemver={
        'bugtracker_url': url + '/issues',
    },
    version="0.9.1",
    author="Olivier Orabona",
    author_email="olivier.orabona@gmail.com",
    description="Authenticate SSH users keys with GitHub",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=url,
    packages=packages,
    setup_requires=setup_requires,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require=extras_require,
    entry_points={
        'console_scripts': [
            'github-ssh = github_ssh_auth.cli:cli',
            'github-ssh-update = github_ssh_auth.cli:update',
            'github-ssh-auth = github_ssh_auth.cli:auth',
            # 'github-ssh-init = github_ssh_auth.cli:init',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Topic :: System :: Systems Administration",
        "Topic :: System :: Systems Administration :: Authentication/Directory",
        "Topic :: System :: Shells",
        "Topic :: Security"
    ],
)
