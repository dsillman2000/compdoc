import argparse
import os

import yaml

import compdoc.compiler
import compdoc.parser

if __name__ == "__main__":

    arg_parser = argparse.ArgumentParser(description="CompDoc CLI")
    cmd_parser = arg_parser.add_subparsers()

    init_parser = cmd_parser.add_parser('init', help='Initialize CompDoc on a Python project. Should be called from the'
                                        ' root folder of the project.')
    init_parser.add_argument('init_path', type=str, help='Location to initialize CompDoc', default=os.getcwd())

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
                print(mod, path)
                f.write(f'\n - {mod}: {path}')
            print('CompDoc initialized in ' + os.path.join(arguments.init_path, '.compdoc.yml'))

    elif arguments.compile_path:

        if arguments.config_path is None:
            config_path = os.path.join(os.path.dirname(arguments.compile_path), '.compdoc.yml')
        else:
            config_path = arguments.config_path

        if not os.path.exists(config_path):
            print("ERROR: Couldn't find CompDoc yaml configuration file in compilation directory: %s" % \
                arguments.compile_path)
            exit(1)

        with open(config_path, 'r') as cf:
            print('config path = %s' % config_path)
            config_dict = yaml.load(cf, yaml.BaseLoader)
            print(config_dict)

        if not os.path.exists(arguments.compile_path):
            print("ERROR: Couldn't find CompDoc markdown file to compile: %s" % arguments.compile_path)
            exit(1)

        try:
            compdoc.compiler.compile_compdoc_mdj2(arguments.compile_path, config_dict, out_path=arguments.out_path)
        except Exception as e:
            raise(e)
        
