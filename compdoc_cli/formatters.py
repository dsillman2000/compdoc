import fnmatch
import glob
import os


def load_formatters(out_folder: str, load_pattern: str = '*') -> dict[str, str]:

    if not os.path.exists(out_folder):
        os.mkdir(out_folder)

    formatter_files = glob.glob('default_formatters/' + load_pattern, root_dir=os.path.dirname(__file__))
    print('formatter files = %s' % formatter_files)
    
    formatter_basenames = { os.path.basename(ff): ff for ff in formatter_files }
    matching_formatters = { k: v for k, v in formatter_basenames.items() if fnmatch.fnmatch(k, load_pattern) }

    for basename, path in matching_formatters.items():
        path = os.path.join('compdoc_cli', path)
        with open(path, 'r') as formatter_src:
            with open(os.path.join(out_folder, basename), 'w') as formatter_dst:
                formatter_dst.write(formatter_src.read())

    return { 
        basename[:basename.find('.')]: os.path.join(out_folder, basename) 
        for basename in matching_formatters 
    }