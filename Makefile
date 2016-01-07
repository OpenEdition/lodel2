all: check doc pip

check:
	python -m unittest -v

doc: cleandoc
	doxygen

pip: cleanpycache
	pip install --upgrade -r requirements.txt

.PHONY: check doc clean cleanpyc cleandoc cleanpycache

cleandoc:
	-rm -Rfv ./doc/
cleanpyc:
	-find ./ |grep -E "\.pyc$$" |xargs rm -fv 2>/dev/null
cleanpycache: cleanpyc
	-find ./ -type d |grep '__pycache__' | xargs rmdir -fv 2>/dev/null

clean: cleanpyc cleandoc cleanpycache
