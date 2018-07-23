#!/usr/bin/env python3

import argparse
import io
import jinja2
import markdown
import os
import sys
import yaml

argparser = argparse.ArgumentParser()

argparser.add_argument(
    'htdocs',
    default='htdocs/',
    help='Directory of htdocs. Default: "%(default)s"',
)

argparser.add_argument(
    'templates',
    default='templates/',
    help='Directory of Jinja2 templates. Default: "%(default)s"',
)

args = argparser.parse_args()

global_variables = {}

try:
    if os.stat('globals.yml'):
        global_variables = yaml.load(open('globals.yml', 'r', encoding='utf-8').read())
except IOError as e:
    exit('Error reading globals.yml')

jinja2_env = jinja2.Environment(
    loader=jinja2.PackageLoader('build'),
)

for root, dirs, files in os.walk(args.htdocs):
    for file in files:
        if not file.endswith('.html.yml'):
            continue

        path = '/'.join([root, file])

        try:
            source = yaml.load(open(path, 'r', encoding='utf-8').read())
        except IOError as e:
            exit('Error reading source "{}" ({})'.format(path, e))


        if source['template'] is None:
            exit('No template defined in "{}"'.format(path))

        template = jinja2_env.get_template(
            source['template'],
            globals=global_variables,
        )

        variables = {}

        for k, v in source.items():
            if k.startswith('markdown_'):
                variables[k[len('markdown_'):]] = markdown.markdown(v)
            else:
                variables[k] = v

        output = path[:-len('.yml')]

        out = open(output, 'w')
        out.write(template.render(variables))
        out.close()
