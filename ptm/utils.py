# import sys
import yaml
import os.path
import sys

from collections import defaultdict

BASE_DIR = os.path.dirname(__file__)
DEFAULT_SETTINGS_FILE = os.path.join(BASE_DIR, 'config', 'defaults.yaml')


def python_version_gte(target):
    return sys.version_info >= target


def read_settings(home_settings):
    with open(DEFAULT_SETTINGS_FILE, 'r') as stream:
        settings = yaml.load(stream)
    try:
        with open(home_settings, 'r') as stream:
            settings.update(yaml.load(stream))
    except FileNotFoundError:
        pass

    try:
        current_dir_settings = os.path.join(BASE_DIR, 'settings.yaml')
        with open(current_dir_settings, 'r') as stream:
            settings.update(yaml.load(stream))
    except FileNotFoundError:
        pass
    return settings


def list_subdirs(path):
    for directory in os.listdir(path):
        subpath = os.path.join(path, directory)
        if os.path.isdir(subpath):
            yield directory, subpath


def templates():
    type_dirs = [os.path.join(BASE_DIR, 'templates')]
    available_templates = defaultdict(set)
    for type_dir in type_dirs:
        for type_name, path in list_subdirs(type_dir):
            for template_name, _ in list_subdirs(path):
                available_templates[type_name].add(template_name)
    yield from available_templates.items()


def get_source(maintype, subtype):
    return os.path.join(BASE_DIR, 'templates', maintype, subtype)


def get_factory_from_template(maintype):
    path = os.path.join(BASE_DIR, 'templates', maintype, 'factory.py')
    if (python_version_gte((3, 4))):
        # Python 3.5 code in this block
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "{}.factory".format(maintype), path)
        foo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(foo)
        return foo
    elif (python_version_gte((3, 0))):
        from importlib.machinery import SourceFileLoader
        foo = SourceFileLoader(
            "{}.factory".format(maintype), path).load_module()
        return foo
    else:
        # Python 2 code in this block
        import imp
        foo = imp.load_source("maintype.factory", path)
        return foo


def get_factory_from_module(modulename):
    import importlib
    foo = importlib.import_module('ptm.factories.{}'.format(modulename))
    return foo
