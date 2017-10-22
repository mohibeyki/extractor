import os
import subprocess

import yaml

from functions import extract_function_proto, extract_function
from generators import gcc_cmd, get_indent_cmd

info_file = open("config.yaml", 'r')
arg_info = yaml.load(info_file)['functions']
info_file.close()

os.system(gcc_cmd)
os.system(get_indent_cmd())

functions = []
ctags_output = subprocess.check_output([
    'ctags',
    '-x',
    '-u',
    '--c-types=fp',
    'generated/preprocessed.c'
]).decode('utf-8').splitlines()
first_function = int(ctags_output[0].split()[2])

for line in ctags_output:
    info = line.split()

    if info[1] == 'function' and info[0] != 'main':
        functions.append({
            'function': info[0],
            'line': info[2],
            'proto': extract_function_proto(line)
        })

with open('generated/preprocessed.c', 'r') as source:
    source_lines = source.readlines()
    for func in functions:
        extract_function(
            source_lines,
            first_function - 2,
            func['function'],
            int(func['line']),
            arg_info[func['proto']]
        )
