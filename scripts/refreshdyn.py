#-*- coding: utf-8 -*-

import sys
import admin

def usage():
    print("""Usage : %s em_filename [output_filename] [translator]

    em_filename \tThe file where the editorial model is stored
    output_filename \tThe file where we should write the dynamic leapi code. If - print to stdout
    translator \t\tThe translator to use to read the editorial model file em_filename
""" % sys.argv[0])

if __name__ == '__main__':
    if len(sys.argv) < 2 or len(sys.argv) > 4:
        usage()
        exit(1)
    filename = sys.argv[1]
    output_file = 'lodel/leapi/dyncode.py' if len(sys.argv) < 3 else sys.argv[2]
    translator = 'picklefile' if len(sys.argv) < 4 else sys.argv[3]

    if output_file == '-':
        print(admin.generate_dyncode(filename, translator))
    else:
        admin.refresh_dyncode(filename, translator, output_file)

