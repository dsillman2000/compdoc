import argparse
import os

import yaml
from compdoc_cli import formatters

import compdoc.compiler
import compdoc.parser


def cli():

    arg_parser = argparse.ArgumentParser(description="CompDoc CLI")
    cmd_parser = arg_parser.add_subparsers()

    init_parser = cmd_parser.add_parser('init', help='Initialize CompDoc on a Python project. Should be called from the'
                                        ' root folder of the project.')
    init_parser.add_argument('init_path', type=str, help='Location to initialize CompDoc', default=os.getcwd())
    init_parser.add_argument('-f --formatters', type=str, help='Pattern to select default formatters by name', 
                             default='*', dest='formatters')

    compile_parser = cmd_parser.add_parser('compile', help='Compile a markdown-Jinja file, including its CompDoc '
                                           'directives.')
    compile_parser.add_argument('compile_path', type=str, help='Path to the markdown-Jinja file to compile.',
                                default=os.path.join(os.getcwd(), 'README.md.j2'))
    compile_parser.add_argument('--config-path', type=str, help='Path to the .compdoc.yml config file, if not in the '
                                'same directory as the compile path.', default=None)
    compile_parser.add_argument('--out-path', type=str, help='Path to put compiled markdown file.', default=None)

    arguments = arg_parser.parse_args()

    if hasattr(arguments, 'init_path') and arguments.init_path:

        if os.path.exists(os.path.join(arguments.init_path, '.compdoc.yml')):
            confirm = input('Overwrite existing .compdoc.yml? (y/n) ')
            if confirm.strip().lower() != 'y':
                exit(0)

        with open(os.path.join(arguments.init_path, '.compdoc.yml'), 'w') as f:
            f.write('modules:')
            for mod, path in compdoc.parser.index_modules(arguments.init_path).items():
                if mod.endswith('__init__'):
                    continue
                print(mod, '\t', path)
                f.write(f'\n  {mod}: {path}')
            formatter_folder = os.path.join(arguments.init_path, 'compdoc-formatters')
            f.write('\n\nformatters:')
            for formatter, path in formatters.load_formatters(formatter_folder, arguments.formatters).items():
                print(formatter, path)
                f.write(f'\n  {formatter}: {path.removeprefix(arguments.init_path + "/")}')
            print('CompDoc initialized in ' + os.path.join(arguments.init_path, '.compdoc.yml'))

    elif arguments.compile_path:
        
        project_folder = os.path.dirname(arguments.compile_path)

        if arguments.config_path is None:
            config_path = os.path.join(project_folder, '.compdoc.yml')
        else:
            config_path = arguments.config_path

        if not os.path.exists(config_path):
            print("ERROR: Couldn't find CompDoc yaml configuration file in compilation directory: %s" % \
                arguments.compile_path)
            exit(1)

        with open(config_path, 'r') as cf:
            config_dict = yaml.load(cf, yaml.BaseLoader)

        """CWD correction"""
        config_dict['modules'] = { 
            mod: os.path.join(project_folder, path) for mod, path in config_dict['modules'].items() 
        }
        config_dict['formatters'] = {
            formatter: os.path.join(project_folder, path) for formatter, path in config_dict['formatters'].items()
        }

        if not os.path.exists(arguments.compile_path):
            print("ERROR: Couldn't find CompDoc markdown file to compile: %s" % arguments.compile_path)
            exit(1)

        try:
            compdoc.compiler.compile_compdoc_mdj2(arguments.compile_path, config_dict, out_path=arguments.out_path)
        except Exception as e:
            raise(e)
        
