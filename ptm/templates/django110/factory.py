import os
import shutil
import hashlib
import time
import random
from jinja2 import Template
from ptm.factories.base import BaseAppFactory

# Use the system PRNG if possible
try:
    random = random.SystemRandom()
    using_sysrandom = True
except NotImplementedError:
    import warnings
    warnings.warn('A secure pseudo-random number generator is not available '
                  'on your system. Falling back to Mersenne Twister.')
    using_sysrandom = False


def get_random_string(length=12,
                      allowed_chars='abcdefghijklmnopqrstuvwxyz'
                                    'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
    """
    Returns a securely generated random string.

    The default length of 12 with the a-z, A-Z, 0-9 character set returns
    a 71-bit value. log_2((26+26+10)^12) =~ 71 bits
    """
    if not using_sysrandom:
        # This is ugly, and a hack, but it makes things better than
        # the alternative of predictability. This re-seeds the PRNG
        # using a value that is hard for an attacker to predict, every
        # time a random string is required. This may change the
        # properties of the chosen random sequence slightly, but this
        # is better than absolute predictability.
        random.seed(
            hashlib.sha256(
                ("%s%s" % (random.getstate(), time.time())).encode('utf-8')
            ).digest())
    return ''.join(random.choice(allowed_chars) for i in range(length))


def get_random_secret_key():
    """
    Return a 50 character random string usable as a SECRET_KEY setting value.
    """
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    return get_random_string(50, chars)


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

    def new_context(self, settings_context, runtime_context=None):
        base_context = super().new_context(settings_context, runtime_context)
        base_context.update({
            'camel_case_name': self.app_name.replace('_', ' ').title(),
            'docs_version': '1.10',
            'django_version': '1.10',
            'secret_key': get_random_secret_key(),
            'camel_case_app_name': self.app_name
                                   .replace('_', ' ')
                                   .title()
                                   .replace('', ''),
        })
        return base_context
