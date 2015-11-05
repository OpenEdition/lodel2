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

** Generate the code for LeObject API

```python
# -*- coding: utf-8 -*-

from EditorialModel.model import Model
from leobject.lefactory import LeFactory
from EditorialModel.backend.json_backend import EmBackendJson
from leobject.datasources.ledatasourcesql import LeDataSourceSQL

OUTPUT = 'leobject/dyn.py'

em = Model(EmBackendJson('EditorialModel/test/me.json'))

pycode = LeFactory.generate_python(EmBackendJson, {'json_file':'EditorialModel/test/me.json'}, LeDataSourceSQL, {})

print(pycode)

with open(OUTPUT, 'w+') as fp:
    fp.write(pycode)
```
