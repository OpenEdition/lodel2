python=python3

all: dyncode

dyncode:
	$(python) -c 'import lodel_admin; lodel_admin.refresh_dyncode()'

init_db: dyncode
	$(python) -c 'import lodel_admin; lodel_admin.init_all_dbs()'
