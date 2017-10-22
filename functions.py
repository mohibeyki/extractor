import os
import subprocess
import time

from files import remove_bswap
from generators import get_value, get_multidim_value, get_indent_cmd, par_cmd


def extract_function_proto(line):
    start = line.find('preprocessed.c')
    if start == -1:
        return ''
    start += 14
    proto = line[start:].strip()
    return proto


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
        proc = subprocess.Popen('/bin/bash', stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        proc.communicate(par_cmd.format(filename).encode('utf-8'))
        remove_bswap(filename)
        os.system('gcc {} -O2 -fopenmp -o {}'.format(filename, filename + '.out'))
        starting_time = time.time() * 1000
        os.system('./{}.out > /dev/null 2> /dev/null'.format(filename))
        print('{:.5f}ms\t{}'.format(time.time() * 1000 - starting_time, function_name))


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