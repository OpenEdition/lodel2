all: check doc pip

# Running unit tests
check:
	python -m unittest -v

# Rule to update libs
pip: cleanpycache
	pip install --upgrade -r requirements.txt

#
# Documentation rules
#
graphviz_images_path = doc/img/graphviz

doc: cleandoc docimages refreshdyn
	doxygen

# Generating graphviz images
docimages:
	cd $(graphviz_images_path); make

refreshdyn:
	python refreshdyn.py &>/dev/null

#
# Cleaning rules
#
.PHONY: check doc clean cleanpyc cleandoc cleanpycache cleandyn cleandocimages

clean: cleanpyc cleandoc cleanpycache cleandocimages cleandyn

# Documentation cleaning
cleandoc:
	-rm -Rfv ./doc/html ./doc/doxygen_sqlite3.db

cleandocimages:
	cd $(graphviz_images_path); make clean

# Python cleaning
cleanpyc:
	-find ./ |grep -E "\.pyc$$" |xargs rm -fv 2>/dev/null
cleanpycache: cleanpyc
	-find ./ -type d |grep '__pycache__' | xargs rmdir -fv 2>/dev/null

cleandyn:
	-rm leapi/dyn.py

