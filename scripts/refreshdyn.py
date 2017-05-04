# 
# This file is part of Lodel 2 (https://github.com/OpenEdition)
#
# Copyright (C) 2015-2017 Cléo UMS-3287
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


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

