First test installation :

- use python 3.4

** install dependencies
  pip install -r requirements.txt

** create local config in Lodel/settings/locale.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'lodel2',
        'USER': 'lodel',
        'PASSWORD': 'lodel',
        'HOST': 'localhost',
    }
}

** create DATABASES
  mysql
  > CREATE DATABASE `lodel2`  CHARACTER SET utf8 COLLATE utf8_general_ci;
  > GRANT ALL ON `lodel2`.* TO "lodel"@"localhost";

** Apply patch(es) for django …
 - makemigrations_interactive_rename.patch => fix makemigrations interactive parameter
  cd path/to/django/
  patch -p2 < /path/to/lodel2/makemigrations_interactive_rename.patch

** create tables for django

if not clean :
  mysql
  > DROP DATABASE `lodel2`;
  recreate database
  rm -rf LodelTestInstance/migrations/

  ./manage.py makemigrations --empty LodelTestInstance
  ./manage.py migrate
