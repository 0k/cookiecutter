#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
cookiecutter.find
-----------------

Functions for finding Cookiecutter templates and other components.
"""

import logging
import os

from .exceptions import NonTemplatedInputDirException


def find_template(repo_dir):
    """
    Determines which child directory of `repo_dir` is the project template.

    :param repo_dir: Local directory of newly cloned repo.
    :returns project_template: Relative path to project template.
    """

    logging.debug('Searching {0} for the project template.'.format(repo_dir))

    repo_dir_contents = os.listdir(repo_dir)

    project_template = None
    candidates = [item for item in repo_dir_contents
                  if '{{' in item and '}}' in item]
    if len(candidates) == 0:
        raise NonTemplatedInputDirException("No template directory found.")
    if len(candidates) > 1:
        raise NonTemplatedInputDirException("Too Much Candidates.")

    project_template = os.path.join(repo_dir, candidates[0])

    logging.debug(
        'The project template appears to be {0}'.format(project_template)
    )
    return project_template
