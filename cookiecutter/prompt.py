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

from .compat import iteritems, read_response, is_string
from jinja2.environment import Environment


def prompt_field(field, help_txt, regex=None, default=None, optional=False):
    """Prompt for value of one field"""

    if default is not None:
        prompt = '{0} (default is "{1}")? '.format(help_txt, default)
    elif optional:
        prompt = '{0} (optional) ? '.format(help_txt)
    else:
        prompt = '{0} ? '.format(help_txt)

    try:
        reg = re.compile('^%s$' % regex) if regex else None
    except Exception, e:
        print("Invalid regex for field %s: %s\n%s"
              % (field, regex, e.message))
        exit(1)

    while True:
        ans = read_response(prompt).strip()
        if ans == '':
            if optional:
                return None
            if default is not None:
                ans = default
        if not reg:
            return ans
        if reg.search(ans):
            return ans

        print("Bad value. Please try to match %r..."
              % regex)


def prompt_for_config(context, no_input=False, use_defaults=False):
    """
    Prompts the user to enter new config, using context as a source for the
    field names and sample values.

    :param no_input: Prompt the user at command line for manual configuration?
    """
    cookiecutter_dict = {}
    env = Environment()

    def render(s):
        return env.from_string(s).render(
            cookiecutter=cookiecutter_dict,
            cc=cookiecutter_dict)

    meta = context.get('__meta__', {})
    keys = meta.keys() if meta else context.keys()
    for key in keys:
        dsc = meta.get(key, None)
        raw = context.get(key, None)
        if raw is not None:
            raw = raw if is_string(raw) else str(raw)
        else:
            raw = meta.get("default", None)
        default = render(raw) if raw is not None else None

        if no_input or (use_defaults and default is not None):
            value = default
        else:
            value = prompt_field(
                field=key,
                help_txt=render(dsc["help"]) if dsc and "help"in dsc else key,
                default=default,
                optional=dsc and "default" in dsc and dsc["default"] is None,
                regex=dsc["regex"] if "regex" in dsc else None)

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
