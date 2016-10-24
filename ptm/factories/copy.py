import shutil
import sys
import os.path
from ptm.factories.base import BaseAppFactory


class AppFactory(BaseAppFactory):
    def run(self):
        dest_dir = os.path.join(self.dest, self.app_name)
        try:
            shutil.copytree(self.source, dest_dir)
        except FileExistsError:
            print(
                'Target directory exists: {dest}, skipping!'.format(
                    dest=self.dest),
                file=sys.stderr)
