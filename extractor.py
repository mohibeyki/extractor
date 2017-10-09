import os
import sys
import subprocess
import random

import yaml

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
    first = proto.find('(')
    return proto[:first - 1] + proto[first:]


def get_random_range(value_range):
    size = str(ranges[value_range][1] - ranges[value_range][0])
    return 'rand() % ' + size + ' + ' + str(ranges[value_range][0])


def get_value_range(value_range):
    return str(random.randint(*ranges[value_range]))


def get_value(arg):
    if 'value' in arg:
        return str(arg['value']) + ';'
    return get_value_range(arg['range']) + ';'


def get_malloc(var_type, dims, size):
    return 'malloc(sizeof(' + var_type + "".join(['*' for _ in range(dims - 1)]) + ') * ' + size + ');'


def get_for(dims, sizes, name, var_type, value_range, level=0):
    if level == dims:
        return ''
    i = str(level)
    size = str(sizes[level])
    cmd = 'for (i' + i + ' = 0; i' + i + ' < ' + size + '; i' + i + '++)\n{\n'

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
    definition += '\n'
    definition += '{\n'

    for i in range(dims):
        definition += 'int i' + str(i) + ';\n'

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
        call += ','.join([arg.keys()[0] for arg in args['args']])
    call += ');\n'
    return call


def extract_function(lines, first, function_name, line_number, proto, function_args):
    start = 0 if line_number < 2 else line_number - 2
    counter = 0
    with open('generated/' + function_name + '.c', 'w') as output:
        for i in range(0, first):
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


os.system('gcc-7 -fpreprocessed -P -dD -E ' + sys.argv[1] + ' > generated/preprocessed.c')
os.system('gindent generated/preprocessed.c')

functions = []
ctags_output = subprocess.check_output(['ctags', '-x', '-u', '--c-types=fp', 'generated/preprocessed.c']).splitlines()
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
            func['proto'],
            arg_info[func['proto']]
        )
