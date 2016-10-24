import datetime
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
        raise NotImplementedError
