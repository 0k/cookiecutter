## From: http://stackoverflow.com/questions/5121931/in-python-how-can-you-load-yaml-mappings-as-ordereddicts

import logging
import yaml
import json

from collections import OrderedDict


def ordered_load(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
    class OrderedLoader(Loader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)


def load_from_yaml(f):
    obj = ordered_load(f, yaml.SafeLoader)
    if "context" in obj and isinstance(obj["context"], dict):
        return {"__meta__": obj["context"]}
    return obj


PARSERS = [
    ('yml', load_from_yaml),
    ('json', lambda f: json.load(f, object_pairs_hook=OrderedDict)),
]


def load_context_from_file(context_file):
    """Load given file"""

    ext = context_file.rsplit(".", 1)[-1]
    parser = dict(PARSERS)[ext]

    file_handle = file(context_file)

    try:
        obj = parser(file_handle)
    except Exception, e:
        logging.error(
            "Error while parsing file %s:\n%s",
            context_file,
            "  " + str(e.message).replace("\n", "\n  "))
        exit(1)
    return obj
