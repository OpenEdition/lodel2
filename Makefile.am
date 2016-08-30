SUBDIRS=lodel

#python=/usr/bin/env python3
python=@PYTHON@
dyncode_filename='lodel/leapi/dyncode.py'

# Doxygen doc generation targets
doc:
	test -z "@DOCOK@" && echo -e "\n\nUnable to generate documentation. See ./configure output for details\n\n" >&2 || make generate-doc

generate-doc: clean doc_graphviz
	doxygen

doc_graphviz:
	cd doc/img/graphviz; make

# Test em update ( examples/em_test.pickle )
em_test: em_test.py
	$(python) em_test.py

# generate leapi dynamic code
dyncode: examples/em_test.pickle
	$(python) scripts/refreshdyn.py examples/em_test.pickle $(dyncode_filename) && echo -e "\n\nCode generated in $(dyncode_filename)"

# run tests
tests:
	./runtest -v

check: tests
checks: tests

#Cleaning documentation and dyncode
clean-local: cleandoc
	-rm -R doc/html doc/doxygen_sqlite3.db
cleandoc:
	-rm $(dyncode_filename)

.PHONY: cleandoc tests doc
