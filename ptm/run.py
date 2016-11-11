#!/usr/bin/env python
import click
import os
from sys import exit
from pprint import pformat

from .utils import (
    templates,
    get_source,
    template_paths,
    get_factory_from_template,
    get_factory_from_module,
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

    try:
        if factory:
            factory_module = get_factory_from_module(factory)
        else:
            for template_type, path in template_paths(additional_dirs):
                if template_type == maintype:
                    factory_module = get_factory_from_template(path)
                    break
            else:
                click.echo(
                    'ERROR: factory not found:{}'.format(maintype),
                    err=True)
                exit(1)
    except FileNotFoundError:
        click.echo('ERROR: factory not found:{}'.format(maintype), err=True)
        exit(1)

    source_dir = get_source(maintype, subtype, path)
    app_factory = factory_module.AppFactory(
        app_name,
        source_dir, current_dir,
        ctx.obj['SETTINGS'].get('context', {})
    )
    app_factory.run()
    click.echo('Done!')


@main.command(short_help='List all available template types and subtypes')
@click.pass_context
def list(ctx):
    additional_dirs = ctx.obj['SETTINGS'].get('templates', [])
    for template_type, template_obs in templates(additional_dirs):
        click.echo('{}:'.format(template_type))
        for template in template_obs:
            click.echo('\t{} - ({})'.format(template.name, template.path))


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
    current_dir = os.getcwd()
    try:
        if factory:
            factory_module = get_factory_from_module(factory)
        else:
            factory_module = get_factory_from_template(maintype)
    except FileNotFoundError:
        click.echo(
            'ERROR: factory not found:{}'.format(maintype),
            err=True)
        exit(1)
    source = get_source(maintype, subtype)
    app_factory = factory_module.AppFactory(
        app_name,
        source, current_dir,
        {}
    )
    click.echo(app_factory.new_context(ctx.obj['SETTINGS'].get('context', {})))


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
