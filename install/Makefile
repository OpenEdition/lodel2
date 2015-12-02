all:

refreshdyn:
	python -c "import utils; utils.refreshdyn()"

dbinit:
	python -c "import utils; utils.db_init()"

.PHONY: clean cleanpycache cleanpyc refreshdyn

clean: cleanpycache

cleanpyc:
	-@rm -v *.pyc

cleanpycache: cleanpyc
	-@rm -vR __pycache__
