dyncode_filename='lodel/leapi/dyncode.py'

all: tests doc dyncode

# generate doxygen documentation
doc: cleandoc doc_graphviz
	doxygen

doc_graphviz:
	cd doc/img/graphviz; make

# Test em update ( examples/em_test.pickle )
em_test:
	python3 em_test.py

# generate leapi dynamic code
dyncode: clean_dyn em_test
	python3 scripts/refreshdyn.py examples/em_test.pickle $(dyncode_filename) && echo -e "\n\nCode generated in $(dyncode_filename)"

# run tests
tests:
	./runtest -v

.PHONY: clean clean_dyn cleandoc cleanpyc tests

clean: clean_dyn cleandoc cleanpyc

cleanpyc:
	-find ./ |grep -E "\.pyc$$" |xargs rm -f 2>/dev/null
cleanpycache:
	-find ./ -type d |grep '__pycache__' | xargs rmdir -f 2>/dev/null

cleandoc:
	-rm -R doc/html doc/doxygen_sqlite3.db

clean_dyn:
	-rm $(dyncode_filename)
	
