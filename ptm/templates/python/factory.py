import os
import shutil
from jinja2 import Template
from ptm.factories.base import BaseAppFactory


class AppFactory(BaseAppFactory):
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
