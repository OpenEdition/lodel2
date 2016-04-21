Local configuration :
	First of all copy the settings.ini to settings_local.ini and replace values by correct path

Doxygen documentation generation :
	doxygen

Dynamic code generation :
	python3 scripts/refreshdyn.py examples/em_test.pickle OUTPUTFILE.py

Instance creation :
	Use the script in scripts/create_instance.sh

	Usage : scripts/create_instance.sh instance_name instance_dir [lodel_libdir]
