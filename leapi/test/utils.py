import tempfile
import shutil
import sys

from EditorialModel.model import Model
import leapi
from EditorialModel.backend.json_backend import EmBackendJson
from leapi.datasources.dummy import DummyDatasource
from leapi.lefactory import LeFactory



genepy_args = {
    'model' : Model(EmBackendJson(json_file = 'EditorialModel/test/me.json')),
    'datasource_cls': DummyDatasource,
    'datasource_args': {}
}

def tmp_load_factory_code(name='dyncode'):
    tmpdir = tempfile.mkdtemp('_lodel2_test_dyncode')
    fname = tmpdir+'/%s.py'%name
    
    sys.path.append(tmpdir)
    fact = LeFactory(fname)
    fact.create_pyfile(**genepy_args)

    return tmpdir


def cleanup(tmpdir):
    shutil.rmtree(tmpdir)
