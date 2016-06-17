Local configuration :
	First of all copy the settings.ini to settings_local.ini and replace values by correct path

Dependencies :
	with pip : see requierments.txt
	debian stable : python3 python3-lxml python3-jinja2 python3-werkzeug python3-pymongo doxygen graphviz

Doxygen documentation generation :
	doxygen

Dynamic code generation :
	python3 scripts/refreshdyn.py examples/em_test.pickle OUTPUTFILE.py

Instance creation :
	Use the script in scripts/create_instance.sh

	Usage : scripts/create_instance.sh instance_name instance_dir [lodel_libdir]

Instance operations :
	A Makefile is written to allow running most of operations. Existing targets are for the moment :

	make dyncode # Leapi dynamic code creation ( in leapi_dyncode.py in lodel2 instance root dir)
	make db_init # Call migration handlers to tell them to init all needed databases. (note : this target has dyncode as dependencie)
