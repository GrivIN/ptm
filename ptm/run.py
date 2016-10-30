#!/usr/bin/env python
import click
import os
from os.path import (
    expanduser,
    join,
)
from sys import exit, stderr
from pprint import pformat

from .utils import (
    templates,
    get_source,
    template_paths,
    get_factory_from_template,
    get_factory_from_module,
    read_settings,
)

home = expanduser("~")
SETTINGS_FILENAME = '.ptm-settings.yaml'


@click.group()
@click.option('--settings', default=join(home, SETTINGS_FILENAME))
@click.pass_context
def main(ctx, settings):
    ctx.obj = {}
    ctx.obj['SETTINGS'] = read_settings(settings)


@main.command(context_settings=dict(
    ignore_unknown_options=True,
))
@click.argument('app_name')
@click.argument('maintype', default=None, required=False)
@click.argument('subtype', default=None, required=False)
@click.option('--factory', default=None)
@click.pass_context
def create(ctx, maintype, subtype, app_name, factory):
    maintype = maintype or ctx.obj['SETTINGS'].get(
        'default_maintype', 'python')
    subtype = subtype or ctx.obj['SETTINGS'].get(
        'default_subtype', 'app')
    print('Type: {}\nSubtype: {}\nApp name: {}'.format(
        maintype, subtype, app_name))
    current_dir = os.getcwd()
    additional_dirs = ctx.obj['SETTINGS'].get('templates', [])
    factory_module = None
    path = None
    try:
        if factory:
            factory_module = get_factory_from_module(factory)
        else:
            for template_type, path in template_paths(additional_dirs):
                if template_type == maintype:
                    factory_module = get_factory_from_template(path)
                    break
            else:
                print('factory not found:{}'.format(maintype), file=stderr)
                exit(1)
    except FileNotFoundError:
        print('factory not found:{}'.format(maintype), file=stderr)
        exit(1)
    source_dir = get_source(maintype, subtype, path)
    app_factory = factory_module.AppFactory(
        app_name,
        source_dir, current_dir,
        ctx.obj['SETTINGS'].get('context', {})
    )
    app_factory.run()
    print('Done')


@main.command()
@click.pass_context
def list(ctx):
    additional_dirs = ctx.obj['SETTINGS'].get('templates', [])
    for template_type, template_obs in templates(additional_dirs):
        print('{}:'.format(template_type))
        for template in template_obs:
            print('\t{} - ({})'.format(template.name, template.path))


@main.command()
@click.argument('app_name', default='[AppName]')
@click.argument('maintype', default=None, required=False)
@click.argument('subtype', default=None, required=False)
@click.option('--factory', default=None)
@click.pass_context
def context(ctx, maintype, subtype, app_name, factory):
    maintype = maintype or ctx.obj['SETTINGS'].get('maintype', 'python')
    subtype = subtype or ctx.obj['SETTINGS'].get('subtype', 'app')
    current_dir = os.getcwd()
    try:
        if factory:
            factory_module = get_factory_from_module(factory)
        else:
            factory_module = get_factory_from_template(maintype)
    except FileNotFoundError:
        print('factory not found:{}'.format(maintype), file=stderr)
        exit(1)
    source = get_source(maintype, subtype)
    app_factory = factory_module.AppFactory(
        app_name,
        source, current_dir,
        {}
    )
    click.echo(app_factory.new_context(ctx.obj['SETTINGS'].get('context', {})))


@main.command()
@click.pass_context
def settings(ctx):
    click.echo(pformat(ctx.obj['SETTINGS']))


if __name__ == '__main__':
    main()
