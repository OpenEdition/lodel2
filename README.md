First test installation :

- use python 3.4

** install dependencies
  pip install -r requirements.txt

** create local config in settings.py
Copy settings.py.example to settings.py, change the conf to your local settings

** create DATABASES
  mysql
  > CREATE DATABASE `lodel2`  CHARACTER SET utf8 COLLATE utf8_general_ci;
  > GRANT ALL ON `lodel2`.* TO "lodel"@"localhost";
