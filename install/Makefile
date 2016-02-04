all: refreshdyn dbinit dirinit

refreshdyn: cleandyn dyncode
	python -c "import utils; utils.refreshdyn()"

dyncode:
	mkdir dyncode; touch dyncode/__init__.py

dbinit:
	python -c "import utils; utils.db_init()"

dirinit:
	python -c "import utils; utils.dir_init()"

emgraph:
	python -c "import utils; utils.em_graph()"

.PHONY: clean cleanpycache cleanpyc refreshdyn distclean

distclean: clean cleandyn

clean: cleanpycache

cleandyn: cleanpycache
	-@rm -vf dyncode/internal_api.py dyncode/acl_api.py dyncode/__init__.py ; rmdir dyncode

cleanpyc:
	-@rm -vf *.pyc

cleanpycache: cleanpyc
	-@rm -vfR __pycache__
