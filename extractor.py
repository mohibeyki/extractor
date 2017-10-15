import os
import platform
import random
import subprocess
import sys

import time
import yaml

gcc_bin = 'gcc-7' if platform.system().lower() == 'darwin' else 'gcc'
indent_bin = 'astyle -A1 -n > /dev/null'

gcc_cmd = '{} -fpreprocessed -P -dD -E {} > generated/preprocessed.c'.format(gcc_bin, sys.argv[1])
indent_cmd = '{} {}'


def get_indent_cmd(filename='generated/preprocessed.c'):
    return indent_cmd.format(indent_bin, filename)


c_malloc = 'malloc(sizeof({}{}) * {});'
c_for = 'for (i{} = 0; i{} < {}; i{}++)'
c_rand = 'rand() % {} + {}'

info_file = open("config.yaml", 'r')
arg_info = yaml.load(info_file)['functions']
info_file.close()

ranges = {
    'small': (0, 128),
    'big': (1024, 2048)
}


def extract_function_proto(line):
    start = line.find('preprocessed.c')
    if start == -1:
        return ''
    start += 14
    proto = line[start:].strip()
    return proto


def get_random_range(value_range):
    size = str(ranges[value_range][1] - ranges[value_range][0])
    return c_rand.format(size, str(ranges[value_range][0]))


def get_value_range(value_range):
    return str(random.randint(*ranges[value_range]))


def get_value(arg):
    if 'value' in arg:
        return str(arg['value']) + ';'
    return get_value_range(arg['range']) + ';'


def get_malloc(var_type, dims, size):
    return c_malloc.format(var_type, "".join(['*' for _ in range(dims - 1)]), size)


def get_for(dims, sizes, name, var_type, value_range, level=0):
    if level == dims:
        return ''
    i = str(level)
    size = str(sizes[level])
    cmd = c_for.format(i, i, size, i) + '\n{\n'

    cmd += name
    cmd += '[' + ']['.join(['i' + str(j) for j in range(level + 1)]) + '] = '

    if level + 1 < dims:
        cmd += get_malloc(var_type, dims - level, sizes[level + 1]) + '\n'
        cmd += get_for(dims, sizes, name, var_type, value_range, level + 1)
    else:
        if value_range == 'output':
            cmd += '0'
        else:
            cmd += get_random_range(value_range)
        cmd += ';\n'

    cmd += '}\n'
    return cmd


def get_multidim_value(name, arg, dims):
    current_dim = dims
    sizes = str(arg['size']).split('x')
    sizes.append('0')
    definition = get_malloc(arg['type'], current_dim, sizes[dims - current_dim])
    definition += '\n{\n'

    for i in range(dims):
        definition += 'int i{};\n'.format(i)

    definition += get_for(dims, sizes, name, arg['type'], arg['range'])
    definition += '}\n'

    return definition


def parse_args(arg):
    for name in arg:
        definition = arg[name]['type']
        dims = 0
        if 'size' in arg[name]:
            dims = len(str(arg[name]['size']).split('x'))

        for i in range(dims):
            definition += '*'
        definition += ' ' + name + ' = '

        if dims == 0:
            definition += get_value(arg[name]) + '\n'
        else:
            definition += get_multidim_value(name, arg[name], dims)

        return definition


def get_function_call(name, args):
    call = name + "("
    if args is not None:
        call += ','.join([list(arg)[0] for arg in args['args']])
    call += ');\n'
    return call


def extract_function(lines, first, function_name, line_number, function_args):
    start = line_number - 1
    counter = 0
    filename = 'generated/' + function_name + '.c'
    with open(filename, 'w') as output:
        for i in range(0, first + 1):
            output.write(lines[i])

        for i in range(start, len(lines)):
            output.write(lines[i])
            if lines[i].strip() == '{':
                counter += 1
            elif lines[i].strip() == '}':
                counter -= 1
                if counter == 0:
                    break

        output.write('int main()\n{\n')
        if function_args is not None:
            for arg in function_args['args']:
                output.write(parse_args(arg))

        output.write(get_function_call(function_name, function_args))
        output.write('return 0;\n}\n')
        output.close()
        os.system(get_indent_cmd(filename))
        os.system('gcc {} -O2 -o {}'.format(filename, filename + '.out'))
        starting_time = time.time() * 1000
        os.system('./{}.out > /dev/null 2> /dev/null'.format(filename))
        print('{:.5f}ms\t{}'.format(time.time() * 1000 - starting_time, function_name))


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
