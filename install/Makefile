all: refreshdyn dbinit

refreshdyn: distclean
	python -c "import utils; utils.refreshdyn()"

dbinit:
	python -c "import utils; utils.db_init()"

emgraph:
	python -c "import utils; utils.em_graph()"

.PHONY: clean cleanpycache cleanpyc refreshdyn distclean

distclean: clean
	-@rm -vf dynleapi.py

clean: cleanpycache

cleanpyc:
	-@rm -vf *.pyc

cleanpycache: cleanpyc
	-@rm -vfR __pycache__
