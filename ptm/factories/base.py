import os
import sys
import shutil
import datetime
from jinja2 import (
    Template,
    Environment,
    make_logging_undefined,
    FileSystemLoader,
)
from ptm.utils import python_version_gte, list_subdirs

from ptm.settings import SKIP_TEMPLATE_DIRS


class AppTemplate(object):
    def __init__(self, name, path=None):
        self.name = name
        self.path = path

    def __str__(self):
        if self.path:
            return '{0} - ({1})'.format(self.name, self.path)
        else:
            return '{0}'.format(self.name)


class BaseAppFactory(object):
    def __init__(self, path, args):
        self.args = list(args)
        self.path = path

    def setup(self, subtype, app_name, dest):
        self.source = os.path.join(self.path, subtype)
        self.subtype = subtype
        self.app_name = app_name
        self.dest = dest

    def run(self):
        raise NotImplementedError

    def set_context(self, settings_context):
        self.context = self.get_context(settings_context)

    def get_context(self, settings_context):
        return {}

    def submodules(self):
        for template_name, template_path in list_subdirs(self.path):
            if template_name in SKIP_TEMPLATE_DIRS:
                continue
            template = AppTemplate(template_name, template_path)
            yield template


class TemplatedAppFactory(BaseAppFactory):
    def setup(self, subtype, app_name, dest):
        super().setup(subtype, app_name, dest)
        self.source_len = len(self.source)
        self.env = Environment(
            loader=FileSystemLoader(self.source),
            undefined=make_logging_undefined())

    def get_context(self, settings_context):
        context = {
            'now': datetime.datetime.now().isoformat(),
            'app_name': self.app_name,
            'unicode_literals': '' if python_version_gte(3, 0) else
                                '# -*- coding: utf-8 -*-\n'
                                'from __future__ import unicode_literals\n\n'
        }
        settings_context.update(context)
        return settings_context

    def get_source_subpath(self, root):
        source_subpath = root[self.source_len:]
        if source_subpath.startswith('/'):
            source_subpath = source_subpath[1:]
        return source_subpath

    def get_dest_subpath(self, subpath):
        dest_subpath = Template(subpath).render(**self.context)
        return dest_subpath

    def get_dest_path(self, dest_subpath, filename):
        dest_path = os.path.join(
            self.dest, self.app_name, dest_subpath, filename)
        return dest_path

    def makedir(self, dest_subpath):
        dest_dir = os.path.join(self.dest, self.app_name, dest_subpath)
        os.makedirs(dest_dir)

    def process_file(self, root, filename, source_subpath, dest_subpath):
        print('Processing: {}'.format(os.path.join(source_subpath, filename)))
        source_path = os.path.join(root, filename)
        dest_path = self.get_dest_path(dest_subpath, filename)
        if filename.endswith('.ptmt'):
            self.process_template_file(
                source_subpath, filename, dest_path
            )
        else:
            shutil.copyfile(source_path, dest_path)

    def process_template_file(self, subpath, filename, dest_path):
        template = self.env.get_template(
            os.path.join(subpath, filename)
        )
        with open(dest_path[:-5], mode='w') as dest_file:
            dest_file.write(template.render(**self.context))

    def run(self):
        for root, dirs, files in os.walk(self.source):
            source_subpath = self.get_source_subpath(root)
            dest_subpath = self.get_dest_subpath(source_subpath)
            self.makedir(dest_subpath)
            for filename in files:
                self.process_file(root, filename, source_subpath, dest_subpath)


class CopyAppFactory(BaseAppFactory):
    def run(self):
        dest_dir = os.path.join(self.dest, self.app_name)
        try:
            shutil.copytree(self.source, dest_dir)
        except FileExistsError:
            print(
                'Target directory exists: {dest}, skipping!'.format(
                    dest=self.dest),
                file=sys.stderr)
