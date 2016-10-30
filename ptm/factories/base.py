import os
import sys
import shutil
import datetime
from jinja2 import Template
from ptm.utils import python_version_gte


class BaseAppFactory(object):
    def __init__(self, app_name,
                 source, dest,
                 settings_context, runtime_context=None):
        self.app_name = app_name
        self.source = source
        self.dest = dest
        self.context = self.new_context(settings_context, runtime_context)

    def new_context(self, settings_context, runtime_context=None):
        return {}

    def run(self):
        raise NotImplementedError


class TemplatedAppFactory(BaseAppFactory):

    def new_context(self, settings_context, runtime_context=None):
        context = {
            'now': datetime.datetime.now().isoformat(),
            'app_name': self.app_name,
            'unicode_literals': '' if python_version_gte((3, 0)) else
                                '# -*- coding: utf-8 -*-\n'
                                'from __future__ import unicode_literals\n\n'
        }  # TODO: add target python varsion variable for 'unicode_literals'
        context.update(settings_context)
        if runtime_context:
            context.update(runtime_context)
        return context

    def run(self):
        source_len = len(self.source)
        for root, dirs, files in os.walk(self.source):
            subpath = root[source_len:]
            if subpath.startswith('/'):
                subpath = subpath[1:]
            subpath = Template(subpath).render(**self.context)
            dest_dir = os.path.join(self.dest, self.app_name, subpath)
            os.makedirs(dest_dir)
            for filename in files:
                source_path = os.path.join(root, filename)
                dest_path = os.path.join(
                    self.dest, self.app_name, subpath, filename)
                if filename.endswith('.ptmt'):
                    with open(source_path, mode='r') as source_file:
                        template = Template(source_file.read())
                    with open(dest_path[:-5], mode='w') as dest_file:
                        dest_file.write(template.render(**self.context))
                else:
                    shutil.copyfile(source_path, dest_path)


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
