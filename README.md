# Project Templates (boilerplate) Manager
Project Templates Manager is a tool to help create new projects from boilerplate. It preprocess code and setup it to your needs, for example author name and email, license etc.

## Requirements
Project Templates Manager requires click, pyyaml and Jinja2

## Getting It
You can get Project Templates Manager from GitHub and run `setup.py`:

    $ git clone git://github.com/GrivIN/ptm.git
    $ cd ptm
    $ python setup.py install

## Getting Started
Project Templates Manager is a command line tool, to print help type `ptm` or `ptm [COMMAND] --help` to get command specific help.

Before first user set up your own context variables by copying `ptm/config/settings.example.yaml` to your home directory and change values privided by example to you own.

    $ cp ptm/config/settings.example.yaml ~/.ptm-settings.yaml
    $ nano ~/.ptm-settings.yaml

### Start new project
To create new project go to your projects directory (ex. `~/work/projects/`) and type

    $ ptm create [OPTIONS] APP_NAME [MAINTYPE] [SUBTYPE]

`[MAINTYPE]` and `[SUBTYPE]` are optional and if not given defaults from settings file will be used. To see all available type `ptm list`:

    $ ptm list
    django110:
    	app - ([...]/ptm/templates/django110/app)
    	project - ([...]/ptm/templates/django110/project)
    python:
    	app - ([...]/ptm/templates/python/app)

### Setup
You could have up to 4 settings files:
- `ptm/config/defaults.yaml`
- `~/.ptm-settings.yaml`
- `.ptm-settings.yaml` in current directory
- settings file pointed by `--settings` option

Those files are readed in above order and if variable is given in more than one last occurence will be used. Aditionaly `context` variables could be updated by `get_context` method in `[MAINTYPE]/factory.py`

### Create new boilerplate template
To add new boilerplate templates into system, setup `templates` variable in `~/.ptm-settings.yaml` by adding full path to directory (could handle multiple locations) contain additional templates.
- Create subdirectory with yours `[MAINTYPE]` name.
- Create subdirectory inside `[MAINTYPE]` dir with `[SUBTYPE]` as a name, it will contain your boilerplate files. Files without `.ptmt` extension will be not processed by Jinja2 template system.
- Create `factory.py` file inside `[MAINTYPE]` dir with minimal contents:

```python
from ptm.factories.base import TemplatedAppFactory


class AppFactory(TemplatedAppFactory):
    def get_context(self, settings_context):
        return super().get_context(settings_context)

    def run(self):
        return super().run()

```
- run `ptm list` to check you new template is visible.

### Add new context variables

#### Static variables
To set up new context variable you could use `~/.ptm-settings.yaml` for global usage, or `.ptm-settings.yaml` in current directory to company/project specific variables

#### Dynamic variables
To change or add new dynamic context variables you have to create your own factory and overwrite `get_context` method. Check `ptm/templates/django110/factory.py` for more details.
