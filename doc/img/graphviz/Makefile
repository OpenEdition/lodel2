dotfiles := $(wildcard *.dot)
images := $(patsubst %.dot,%.png,$(wildcard *.dot))

all: $(images)
	
%.png: %.dot
	dot -Tpng $< > $@

.PHONY: clean distclean

clean:
	-rm $(images)

distclean: clean
