python=python3

all: dyncode

dyncode:
	$(python) -c 'import lodel_admin; lodel_admin.refresh_dyncode()'

init_db: dyncode
	$(python) -c 'import lodel_admin; lodel_admin.init_all_dbs()'

list_hooks: dyncode
	$(python) -c 'import lodel_admin; lodel_admin.list_registered_hooks()'

refresh_plugins:
	$(python) -c 'import lodel_admin; lodel_admin.update_plugin_discover_cache()'
