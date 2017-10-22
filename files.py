def remove_bswap(filename):
    par_file = filename[:-2] + '.p4a.c'
    with open(par_file, 'r') as input_file:
        input_lines = input_file.readlines()
        with open(filename, 'w') as output_file:
            i = 0
            for line in input_lines:
                if line.strip() == 'static __uint64_t __bswap_64(__uint64_t __bsx)':
                    i = 4
                if i > 0:
                    i -= 1
                    continue
                output_file.write(line)
