import platform
import random
import sys

gcc_bin = 'gcc-7' if platform.system().lower() == 'darwin' else 'gcc'
indent_bin = 'astyle -A1 -n > /dev/null'
par_cmd = '''
source /usr/local/par4all/etc/par4all-rc.sh
p4a {}
'''

c_malloc = 'malloc(sizeof({}{}) * {});'
c_for = 'for (i{} = 0; i{} < {}; i{}++)'
c_rand = 'rand() % {} + {}'

ranges = {
    'small': (0, 128),
    'big': (1024, 2048)
}

gcc_cmd = '{} -fpreprocessed -P -dD -E {} > generated/preprocessed.c'.format(gcc_bin, sys.argv[1])
indent_cmd = '{} {}'


def get_indent_cmd(filename='generated/preprocessed.c'):
    return indent_cmd.format(indent_bin, filename)


def get_value_range(value_range):
    return str(random.randint(*ranges[value_range]))


def get_value(arg):
    if 'value' in arg:
        return str(arg['value']) + ';'
    return get_value_range(arg['range']) + ';'


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


def get_random_range(value_range):
    size = str(ranges[value_range][1] - ranges[value_range][0])
    return c_rand.format(size, str(ranges[value_range][0]))


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
