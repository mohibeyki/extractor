import os
import string

from generators import get_indent_cmd


def get_indent(line):
    count = 0
    for c in line:
        if c in string.whitespace:
            count += 1
        else:
            break
    return count


def is_closing_bracket(line, base_indent):
    if get_indent(line) < base_indent:
        return True
    return line.strip() == '}' and get_indent(line) == base_indent


def count_for_levels(lines, i):
    max_fors = 0
    base_indent = get_indent(lines[i])
    indention_stack = []
    i += 1
    # any command with lower indention than pragma, is not in its block
    while i < len(lines) and not is_closing_bracket(lines[i], base_indent):
        if lines[i].strip().startswith('for('):
            if len(indention_stack) == 0:
                current_fors = 1
            else:
                current_fors = indention_stack[-1][1]

            max_fors = max(max_fors, current_fors)
            # print(i, get_indent(lines[i]), lines[i])
            if len(indention_stack) == 0 or indention_stack[-1][0] < get_indent(lines[i]):
                current_fors += 1
                indention_stack.append((get_indent(lines[i]), current_fors))

        i += 1
    return max_fors


def convert_to_gpu(filename):
    os.system(get_indent_cmd(filename))
    with open(filename, 'r') as file:
        lines = file.readlines()
        size = len(lines)
        print(filename, size)
        for i in range(size):
            if lines[i].strip() == 'int main()':
                break
            if lines[i].strip().startswith('#pragma omp'):
                fors = count_for_levels(lines, i)
                print(fors)
