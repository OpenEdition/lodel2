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
