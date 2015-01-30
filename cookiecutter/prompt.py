#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
cookiecutter.prompt
---------------------

Functions for prompting the user for project info.
"""

from __future__ import unicode_literals
from __future__ import print_function

import sys
import re

from .compat import read_response, is_string
from jinja2.environment import Environment


def prompt_field(field, help_txt, value=None, regex=None,
                 default=None, required=False):
    """Prompt for value of one field

    """

    if default is not None:
        prompt = '{0} (default is "{1}") ? '.format(help_txt, default)
    elif not required:
        prompt = '{0} (optional) ? '.format(help_txt)
    else:
        prompt = '{0} ? '.format(help_txt)

    try:
        reg = re.compile('^%s$' % regex) if regex else None
    except re.error as e:
        print("Invalid regex for field %s: %s\n%s"
              % (field, regex, e.message))
        exit(1)

    while True:
        if value:
            ans = value
        else:
            ans = read_response(prompt).strip()
        if ans == '':
            if not required:
                return None
            if default is not None:
                ans = default
        if not reg:
            return ans
        if reg.search(ans):
            return ans

        print("Bad value for template field '%s'. Please try to match %r..."
              % (field, regex))
        value = None


def prompt_for_config(context, no_input=False, only_missing=None, values=None,
                      with_optional=True):
    """
    Prompts the user to enter new config, using context as a source for the
    field names and sample values.

    :param no_input: Prompt the user at command line for manual configuration?
    """
    if "cookiecutter" in context:
        context = context["cookiecutter"]

    if values is None:
        values = {}

    cookiecutter_dict = {}
    env = Environment()

    def render(s):
        return env.from_string(s).render(
            cookiecutter=cookiecutter_dict,
            cc=cookiecutter_dict)

    meta = context.get('__meta__', {})
    if only_missing is None:
        only_missing = True if meta else False

    keys = meta.keys() if meta else context.keys()
    for key in keys:
        dsc = meta.get(key, {})
        raw = values.get(key, None) or context.get(key, None)
        if key.startswith('_'):
            cookiecutter_dict[key] = raw
            continue
        if raw is not None:
            raw = raw if is_string(raw) else str(raw)
        else:
            raw = dsc.get("default", None)
        default = render(raw) if raw is not None else None

        optional = dsc and "default" in dsc and dsc["default"] is None

        if no_input or \
           (only_missing and default is not None) or \
           (optional and not with_optional):
            value = default
        else:
            value = prompt_field(
                field=key, value=values.get(key, None),
                help_txt=render(dsc["help"]) if dsc and "help" in dsc else key,
                default=default,
                required=not optional,
                regex=dsc["regex"] if dsc and "regex" in dsc else None)

        cookiecutter_dict[key] = value
    return cookiecutter_dict


def query_yes_no(question, default='yes'):
    """
    Ask a yes/no question via `read_response()` and return their answer.

    :param question: A string that is presented to the user.
    :param default: The presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is one of "yes" or "no".

    Adapted from
    http://stackoverflow.com/questions/3041986/python-command-line-yes-no-input
    http://code.activestate.com/recipes/577058/

    """
    valid = {'yes': True, 'y': True, 'ye': True, 'no': False, 'n': False}
    if default is None:
        prompt = ' [y/n] '
    elif default == 'yes':
        prompt = ' [Y/n] '
    elif default == 'no':
        prompt = ' [y/N] '
    else:
        raise ValueError('Invalid default answer: "{0}"'.format(default))

    while True:
        sys.stdout.write(question + prompt)
        choice = read_response().lower()

        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write('Please respond with "yes" or "no" '
                             '(or "y" or "n").\n')
