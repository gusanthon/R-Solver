import subprocess, sys, re, os

def print_matrix(M, out_file, num_ports, adapt_expr, args, custom_args):
    '''Prints a Sage matrix as a C-style 2D array'''

    comment_symbol = '# ' if args.pywdf else '// '
    comments = comment_symbol + 'This scattering matrix was derived using the R-Solver python script (https://github.com/jatinchowdhury18/R-Solver),\n'

    if custom_args:
        args_str = 'r_solver.py '
        args_str += '--datum ' + str(args.datum) + ' '
        args_str += '--adapt ' + str(args.adapted_port) + ' '
        args_str += '--verbose ' + str(args.verbose) + ' '
        args_str += '--out ' + args.out_file.name + ' '
        args_str += args.netlist.name
        args_str += str(args.pywdf) + ' '
        comments += comment_symbol + 'invoked with command: ' + args_str + '\n'
    else:
        args_str = subprocess.list2cmdline(sys.argv[:])
        comments += comment_symbol + 'invoked with command: ' + args_str + '\n'
    
    M_strs = M.str(rep_mapping=lambda a: str(a) + ',')

    if args.pywdf:
        M_strs = M_strs.replace('\n',',\n\t')
        M_strs = comments + 'R.set_S_matrix([' + M_strs + ']\n)'
        
    else:
        prefix = 'const auto S_matrix[' + str(num_ports) + '][' + str(num_ports) + '] = {'
        empty_prefix = ' ' * len(prefix)
        M_strs = M_strs.replace('[', empty_prefix + '{').replace(',]', '},')
        M_strs = comments + prefix + M_strs[len(prefix):-1] + '};'
    

    # C syntax can't do exponents using the '^' operator.
    # This is a stupid hack that assumes all resistors have
    # a 2-character label, e.g. 'Ra'
    count = 0
    for f in re.finditer(re.escape('^2'), M_strs):
        s_ind = f.start() + count
        chars_to_square = M_strs[s_ind-2:s_ind]
        M_strs = M_strs[:s_ind] + '*' + str(chars_to_square) + M_strs[s_ind+2:]
        count += 1

    if out_file is not None:
        if adapt_expr is not None:
            adapt_expr = str(adapt_expr).replace('==', '=')
            M_strs += '\n\n' + adapt_expr
            adapt_var = adapt_expr[:2] 
            M_strs += '\nreturn ' + adapt_var
            if not args.pywdf:
                M_strs += ';'
            
        out_file.write(M_strs)
        cmd = 'open ' + args.out_file.name
        os.system(cmd)

    else:
        print('')
        print('Scattering matrix:')
        print(M_strs)
    
    return M_strs

def print_shape(M):
    '''Prints the shape of a Sage matrix'''
    print((M.nrows(), M.ncols()))

def verbose_print(mat, name):
    print('')
    print(name)
    print(mat)
    print_shape(mat)
