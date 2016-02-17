DYNDIR=dyncode

all: refreshdyn dbinit dirinit

refreshdyn: cleandyn dyncode
	python -c "import utils; utils.refreshdyn()"

dyncode:
	mkdir $(DYNDIR); touch $(DYNDIR)/__init__.py

dbinit:
	python -c "import utils; utils.db_init()"

dirinit:
	python -c "import utils; utils.dir_init()"

emgraph:
	python -c "import utils; utils.em_graph()"

.PHONY: clean cleanpycache cleanpyc refreshdyn distclean

distclean: clean cleandyn

clean: cleanpycache

cleandyn:
	-rm $(DYNDIR)/acl_api.py $(DYNDIR)/internal_api.py $(DYNDIR)/__init__.py 2>/dev/null ; rmdir $(DYNDIR)

cleanpyc:
	-find ./ |grep -E "\.pyc$$" |xargs rm -f 2>/dev/null
cleanpycache: cleanpyc
	-find ./ -type d |grep '__pycache__' | xargs rmdir 2>/dev/null
