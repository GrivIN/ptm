# import sys
import yaml
import os.path
import sys

from ptm.settings import (
    GLOBAL_SETTINGS_FILENAME,
    FACTORY_FILENAME,
    LOCAL_SETTINGS_FILENAME,
    HOME,
)

BASE_DIR = os.path.dirname(__file__)
DEFAULT_SETTINGS_FILE = os.path.join(BASE_DIR, 'config', 'defaults.yaml')


def python_version_gte(*args):
    return sys.version_info >= args


def read_settings(additional_settings):
    with open(DEFAULT_SETTINGS_FILE, 'r') as stream:
        settings = yaml.load(stream)
    try:
        with open(os.path.join(HOME, GLOBAL_SETTINGS_FILENAME), 'r') as stream:
            current_settings = yaml.load(stream)
            current_context = current_settings.pop('context')
            settings.update(current_settings)
            settings['context'].update(current_context)
    except FileNotFoundError:
        pass

    try:
        current_dir = os.getcwd()
        current_dir_settings = os.path.join(
            current_dir, LOCAL_SETTINGS_FILENAME)
        with open(current_dir_settings, 'r') as stream:
            current_settings = yaml.load(stream)
            current_context = current_settings.pop('context')
            settings.update(current_settings)
            settings['context'].update(current_context)
    except FileNotFoundError:
        pass
    if additional_settings:
        try:
            with open(additional_settings, 'r') as stream:
                current_settings = yaml.load(stream)
                current_context = current_settings.pop('context')
                settings.update(current_settings)
                settings['context'].update(current_context)
        except FileNotFoundError:
            pass
    return settings


def list_subdirs(path):
    try:
        for directory in os.listdir(path):
            subpath = os.path.join(path, directory)
            if os.path.isdir(subpath):
                yield directory, subpath
    except FileNotFoundError:
        print(
            'WARNING: templates directory not found:{}'.format(path),
            file=sys.stderr)
    except PermissionError:
        print(
            'WARNING: no permission to templates directory:{}'.format(path),
            file=sys.stderr)


def template_paths(additional_dirs):
    type_dirs = [os.path.join(BASE_DIR, 'templates')]
    if additional_dirs:
        if isinstance(additional_dirs, list):
            type_dirs.extend(additional_dirs)
        else:
            type_dirs.append(additional_dirs)
    for type_dir in type_dirs:
        for type_name, path in list_subdirs(type_dir):
            yield type_name, path


def get_source(maintype, subtype, path=None):
    if path:
        return os.path.join(path, subtype)
    else:
        return os.path.join(BASE_DIR, 'templates', maintype, subtype)


def get_factory_from_template(maintype):
    path = os.path.join(BASE_DIR, 'templates', maintype, FACTORY_FILENAME)
    if (python_version_gte(3, 5)):
        # Python 3.5 code in this block
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "{}.factory".format(maintype), path)
        foo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(foo)
        return foo
    elif (python_version_gte(3, 0)):
        from importlib.machinery import SourceFileLoader
        foo = SourceFileLoader(
            "{}.factory".format(maintype), path).load_module()
        return foo
    else:
        # Python 2 code in this block
        import imp
        foo = imp.load_source("{}.factory".format(maintype), path)
        return foo


def get_factory_from_module(modulename):
    import importlib
    foo = importlib.import_module(modulename)
    return foo


def get_factory(maintype, factory, additional_dirs):
    try:
        if factory:
            factory_module = get_factory_from_module(factory)
        else:
            for template_type, path in template_paths(additional_dirs):
                if template_type == maintype:
                    factory_module = get_factory_from_template(path)
                    return factory_module, path
    except FileNotFoundError:
        pass
    return None, None
