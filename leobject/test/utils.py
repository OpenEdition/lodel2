import tempfile
import shutil
import sys

import EditorialModel
import leobject
from EditorialModel.backend.json_backend import EmBackendJson
from leobject.datasources.dummy import DummyDatasource
from leobject.lefactory import LeFactory



genepy_args = {
    'backend_cls': EmBackendJson,
    'backend_args': {'json_file': 'EditorialModel/test/me.json'},
    'datasource_cls': DummyDatasource,
    'datasource_args': {}
}

def tmp_load_factory_code(name='dyncode'):
    tmpdir = tempfile.mkdtemp('_lodel2_test_dyncode')
    fname = tmpdir+'/%s.py'%name
    with open(fname, 'w+') as dynfp:
        dynfp.write(LeFactory.generate_python(**genepy_args))
    sys.path.append(tmpdir)
    LeFactory.modname = name
    return tmpdir


def cleanup(tmpdir):
    shutil.rmtree(tmpdir)
