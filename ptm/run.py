#!/usr/bin/env python
import click
import os
from sys import exit
from pprint import pformat

from .utils import (
    get_source,
    template_paths,
    get_factory,
    get_factory_from_template,
    read_settings,
    python_version_gte,
)


@click.group()
@click.option('--settings', default=None,
              help='Path to settings file (with filename)')
@click.pass_context
def main(ctx, settings):
    ctx.obj = {}
    ctx.obj['SETTINGS'] = read_settings(settings)


@main.command(short_help='Create new project bones from template')
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
    click.echo('Type: {};\t Subtype: {};\t App name: {};'.format(
        maintype, subtype, app_name))
    current_dir = os.getcwd()
    additional_dirs = ctx.obj['SETTINGS'].get('templates', [])
    factory_module = None
    path = None

    factory_module, path = get_factory(maintype, factory, additional_dirs)
    if not factory_module:
        click.echo('ERROR: factory not found:{}'.format(maintype), err=True)
        exit(1)

    source_dir = get_source(maintype, subtype, path)
    app_factory = factory_module.AppFactory(path)
    app_factory.setup(app_name, source_dir, current_dir)
    app_factory.set_context(ctx.obj['SETTINGS'].get('context', {}))
    app_factory.run()
    click.echo('Done!')


@main.command(short_help='List all available template types and subtypes')
@click.pass_context
def list(ctx):
    additional_dirs = ctx.obj['SETTINGS'].get('templates', [])
    for template_type, path in template_paths(additional_dirs):
        click.echo('{}:'.format(template_type))
        factory_module = get_factory_from_template(path)
        for template in factory_module.AppFactory(path).submodules():
            click.echo(template)


@main.command(short_help='Print template context variables what will be'
                         ' used to create bones')
@click.argument('app_name', default='[AppName]')
@click.argument('maintype', default=None, required=False)
@click.argument('subtype', default=None, required=False)
@click.option('--factory', default=None)
@click.pass_context
def context(ctx, maintype, subtype, app_name, factory):
    maintype = maintype or ctx.obj['SETTINGS'].get('maintype', 'python')
    subtype = subtype or ctx.obj['SETTINGS'].get('subtype', 'app')
    additional_dirs = ctx.obj['SETTINGS'].get('templates', [])
    current_dir = os.getcwd()

    factory_module, path = get_factory(maintype, factory, additional_dirs)
    if not factory_module:
        click.echo('ERROR: factory not found:{}'.format(maintype), err=True)
        exit(1)

    source = get_source(maintype, subtype)
    app_factory = factory_module.AppFactory(path)
    app_factory.setup(app_name, source, current_dir)
    click.echo(app_factory.get_context(ctx.obj['SETTINGS'].get('context', {})))


@main.command(short_help='Print copmuted settings')
@click.pass_context
def settings(ctx):
    click.echo(pformat(ctx.obj['SETTINGS']))


if __name__ == '__main__':
    if not python_version_gte(3, 0):
        click.echo(
            'Python 3.0 or higher is required to run this command',
            err=True)
        exit(1)
    main()
