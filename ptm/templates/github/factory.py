from ptm.factories.base import TemplatedAppFactory
from io import BytesIO
from jinja2 import (
    Environment,
    make_logging_undefined,
    FunctionLoader,
)
import os.path
import urllib.request
import zipfile


class AppFactory(TemplatedAppFactory):
    def setup(self, subtype, app_name, dest):
        super().setup(subtype, app_name, dest)
        self.source_len = len(self.source)
        self.env = Environment(
            loader=FunctionLoader(self.jinja_loader),
            undefined=make_logging_undefined())

    def download(self):
        url_base = 'https://github.com/{user}/{project}/{method}/{branch}'
        if '/' in self.subtype:
            user, project = self.subtype.split('/')
        else:
            user = self.subtype
            project = self.args.pop(0)
        if self.args:
            branch = self.args.pop(0)
        else:
            branch = 'master'
        if self.args:
            method = self.args.pop(0)
        else:
            method = 'zipball'
        url = url_base.format(
            user=user, project=project, branch=branch, method=method)
        with urllib.request.urlopen(url) as response:
            ziped = BytesIO(response.read())
        with zipfile.ZipFile(ziped) as myzip:
            contents = myzip.namelist()
            self.source = contents.pop(0)
            self.source_len = len(self.source)
            for template in contents:
                head, tail = os.path.split(template)
                if tail:
                    self._contents = myzip.read(template)
                    yield head[self.source_len:], tail

    def jinja_loader(self, templatename=None):
        return (self._contents.decode('utf-8'), templatename, True)

    def run(self):
        for source_subpath, filename in self.download():
            dest_subpath = self.get_dest_subpath(source_subpath)
            try:
                self.makedir(dest_subpath)
            except FileExistsError:
                pass
            self.process_file(filename, source_subpath, dest_subpath)

    def process_file(self, filename, source_subpath, dest_subpath):
        print('Processing: {}'.format(os.path.join(source_subpath, filename)))
        dest_path = self.get_dest_path(dest_subpath, filename)
        if filename.endswith('.ptmt'):
            self.process_template_file(
                source_subpath, filename, dest_path
            )
        else:
            with open(dest_path, mode='wb') as dest_file:
                dest_file.write(self._contents)

    def submodules(self):
        yield 'Listing not available - type /username/projectname to download'
