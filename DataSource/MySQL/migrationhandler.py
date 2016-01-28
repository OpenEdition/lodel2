# -*- coding: utf-8 -*-

import copy
import pymysql

from Lodel.settings import Settings

import EditorialModel
import EditorialModel.classtypes
import EditorialModel.fieldtypes
import EditorialModel.fieldtypes.generic
from EditorialModel.fieldtypes.generic import MultiValueFieldType

from DataSource.MySQL import fieldtypes as fieldtypes_utils
from DataSource.MySQL import utils
from DataSource.dummy.migrationhandler import DummyMigrationHandler

# The global MH algorithm is as follow :
# A create_table(table_name, pk_name, pk_opt) method that create a table
# with one pk field
# An add_column(table_name, field_name, field_opt) method that add a column to a table
#
# The create_default_table method will call both methods to create the object and relation tables
#
# Supported operations :
# - EmClass creation
# - EmClass deletion
# - EmField creation
# - EmField deletion
# - rel2type attribute creation
# - rel2type attribute deletion
#
# Unsupported operations :
# - EmClass rename
# - EmField rename
# - rel2type field rename
# - rel2type attribute rename
# - EmFieldType changes
#
# @todo Unified datasources and migration handlers via utils functions


## @brief Modify a MySQL database given editorial model changes
class MysqlMigrationHandler(DummyMigrationHandler):

    ## @brief Construct a MysqlMigrationHandler
    # @param module : sql module
    # @param conn_args dict : A dict containing connection options
    # @param db_engine str : Name of a MySQL db engine (default is InnoDB, don't change it ! ;) ) 
    # @param **kwargs : arguement given to the module.connect() method
    def __init__(self, module=pymysql, conn_args=None, db_engine='InnoDB', **kwargs):
        # Database connection
        self._dbmodule = module
        if conn_args is None:
            conn_args = copy.copy(Settings.get('datasource')['default'])
            self._dbmodule = conn_args['module']
            del conn_args['module']
        self.db_conn = self._dbmodule.connect(**conn_args)
        # Fetch options
        mh_settings = Settings.migration_options
        self.debug = kwargs['debug'] if 'debug' in kwargs else Settings.debug_sql
        self.dryrun = kwargs['dryrun'] if 'dryrun' in kwargs else mh_settings['dryrun']
        self.foreign_keys = kwargs['foreign_keys'] if 'foreign_keys' in kwargs else mh_settings['foreign_keys']
        self.drop_if_exists = kwargs['drop_if_exists'] if 'drop_if_exists' in kwargs else mh_settings['drop_if_exists']
        self.db_engine = db_engine
        #Create default tables
        self._create_default_tables(self.drop_if_exists)

    ## @brief Modify the db given an EM change
    #
    # @note Here we don't care about the relation parameter of _add_column() method because the
    # only case in wich we want to add a field that is linked with the relation table is for rel2type
    # attr creation. The relation parameter is set to True in the add_relationnal_field() method
    # 
    # @param em model : The EditorialModel.model object to provide the global context
    # @param uid int : The uid of the change EmComponent
    # @param initial_state dict | None : dict with field name as key and field value as value. Representing the original state. None mean creation of a new component.
    # @param new_state dict | None : dict with field name as key and field value as value. Representing the new state. None mean component deletion
    # @param engine str : Mysql db engine, should be "InnoDB"
    # @throw EditorialModel.exceptions.MigrationHandlerChangeError if the change was refused
    def register_change(self, em, uid, initial_state, new_state, engine=None):
        if engine is None:
            engine = self.db_engine
        if isinstance(em.component(uid), EditorialModel.classes.EmClass):
            if initial_state is None:
                #EmClass creation
                self.create_emclass_table(em, uid, engine)
            elif new_state is None:
                #EmClass deletion
                self.delete_emclass_table(em, uid)
        elif isinstance(em.component(uid), EditorialModel.fields.EmField):
            emfield = em.component(uid)
            if emfield.rel_field_id is None:
                #non relationnal field
                if initial_state is None:
                    #non relationnal EmField creation
                    if emfield.name not in EditorialModel.classtypes.common_fields.keys():
                        self.add_col_from_emfield(em, uid)
                elif new_state is None:
                    #non relationnal EmField deletion
                    if emfield.name not in EditorialModel.classtypes.common_fields.keys():
                        self.delete_col_from_emfield(em, uid)
            else:
                #relationnal field
                if initial_state is None:
                    #Rel2type attr creation
                    self.add_relationnal_field(em, uid)
                elif new_state is None:
                    #Rel2type attr deletion
                    self.del_relationnal_field(em, uid)

    ## @brief dumdumdummy
    # @note implemented to avoid the log message of EditorialModel.migrationhandler.dummy.DummyMigrationHandler
    def register_model_state(self, em, state_hash):
        pass

    ## @brief Add a relationnal field
    # Add a rel2type attribute
    # @note this function handles the table creation
    # @param edmod Model : EditorialModel.model.Model instance
    # @param rfuid int : Relationnal field uid
    def add_relationnal_field(self, edmod, rfuid):
        emfield = edmod.component(rfuid)
        if not isinstance(emfield, EditorialModel.fields.EmField):
            raise ValueError("The given uid is not an EmField uid")

        r2tf = edmod.component(emfield.rel_field_id)
        tname = self._r2t2table_name(edmod, r2tf)
        pkname, pkftype = self._relation_pk

        #If not exists create a relational table
        self._create_table(
                            tname,
                            pkname,
                            pkftype,
                            self.db_engine,
                            if_exists='nothing',
                            noauto_inc = True,
                        )
        #Add a foreign key if wanted
        if self.foreign_keys:
            self._add_fk(tname, utils.common_tables['relation'], pkname, pkname)
        #Add the column
        self._add_column(tname, emfield.name, emfield.fieldtype_instance(), relation=True)
        #Update table triggers
        self._generate_triggers(tname, self._r2type2cols(edmod, r2tf))

    ## @brief Delete a rel2type attribute
    #
    # Delete a rel2type attribute
    # @note this method handles the table deletion
    # @param edmod Model : EditorialModel.model.Model instance
    # @param rfuid int : Relationnal field uid
    def del_relationnal_field(self, edmod, rfuid):
        emfield = edmod.component(rfuid)
        if not isinstance(emfield, EditorialModel.fields.EmField):
            raise ValueError("The given uid is not an EmField uid")

        r2tf = edmod.component(emfield.rel_field_id)
        tname = self._r2t2table_name(edmod, r2tf)

        if len(self._r2type2cols(edmod, r2tf)) == 1:
            #The table can be deleted (no more attribute for this rel2type)
            self._query("""DROP TABLE {table_name}""".format(table_name=tname))
        else:
            self._del_column(tname, emfield.name)
            #Update table triggers
            self._generate_triggers(tname, self._r2type2cols(edmod, r2tf))

    ## @brief Given an EmField uid add a column to the corresponding table
    # @param edmod Model : A Model instance
    # @param uid int : An EmField uid
    def add_col_from_emfield(self, edmod, uid):
        emfield = edmod.component(uid)
        if not isinstance(emfield, EditorialModel.fields.EmField):
            raise ValueError("The given uid is not an EmField uid")

        emclass = emfield.em_class
        tname = utils.object_table_name(emclass.name)
        self._add_column(tname, emfield.name, emfield.fieldtype_instance())
        # Refresh the table triggers
        cols_l = self._class2cols(emclass)
        self._generate_triggers(tname, cols_l)

    ## @brief Given a class uid create the coressponding table
    # @param edmod Model : A Model instance
    # @param uid int : An EmField uid
    # @param engine str : Db engine (should be "InnoDB")
    def create_emclass_table(self, edmod, uid, engine):
        emclass = edmod.component(uid)
        if not isinstance(emclass, EditorialModel.classes.EmClass):
            raise ValueError("The given uid is not an EmClass uid")
        pkname, pktype = self._object_pk
        table_name = utils.object_table_name(emclass.name)
        self._create_table(
                            table_name,
                            pkname,
                            pktype,
                            engine=engine,
                            noauto_inc = True
        )
        if self.foreign_keys:
            self._add_fk(table_name, utils.common_tables['object'], pkname, pkname)

    ## @brief Given an EmClass uid delete the corresponding table
    # @param edmod Model : A Model instance
    # @param uid int : An EmField uid
    def delete_emclass_table(self, edmod, uid):
        emclass = edmod.component(uid)
        if not isinstance(emclass, EditorialModel.classes.EmClass):
            raise ValueError("The give uid is not an EmClass uid")
        tname = utils.object_table_name(emclass.name)
        # Delete the table triggers to prevent errors
        self._generate_triggers(tname, dict())

        tname = utils.escape_idname(tname)

        self._query("""DROP TABLE {table_name};""".format(table_name=tname))

    ## @brief Given an EmField delete the corresponding column
    # @param edmod Model : an @ref EditorialModel.model.Model instance
    # @param uid int : an EmField uid
    def delete_col_from_emfield(self, edmod, uid):
        emfield = edmod.component(uid)
        if not isinstance(emfield, EditorialModel.fields.EmField):
            raise ValueError("The given uid is not an EmField uid")

        if isinstance(emfield.fieldtype_instance(), MultiValueFieldType):
            return self._del_column_multivalue(emfield)

        emclass = emfield.em_class
        tname = utils.object_table_name(emclass.name)
        # Delete the table triggers to prevent errors
        self._generate_triggers(tname, dict())

        self._del_column(tname, emfield.name)
        # Refresh the table triggers
        cols_l = self._class2cols(emclass)
        self._generate_triggers(tname, cols_l)

    ## @brief Delete a column from a table
    # @param tname str : The table name
    # @param fname str : The column name
    def _del_column(self, tname, fname):
        tname = utils.escape_idname(tname)
        fname = utils.escape_idname(fname)

        self._query("""ALTER TABLE {table_name} DROP COLUMN {col_name};""".format(table_name=tname, col_name=fname))

    ## @brief Construct a table name given a rela2type EmField instance
    # @param edmod Model : A Model instance
    # @param emfield EmField : An EmField instance
    # @return a table name
    def _r2t2table_name(self, edmod, emfield):
        emclass = emfield.em_class
        emtype = edmod.component(emfield.rel_to_type_id)
        return utils.r2t_table_name(emclass.name, emtype.name)

    ## @brief Generate a columns_fieldtype dict given a rel2type EmField
    # @param edmod Model : an @ref EditorialModel.model.Model instance
    # @param emfield EmField : and @ref EditorialModel.fields.EmField instance
    def _r2type2cols(self, edmod, emfield):
        return {f.name: f.fieldtype_instance() for f in edmod.components('EmField') if f.rel_field_id == emfield.uid}

    ## @brief Generate a columns_fieldtype dict given an EmClass
    # @param emclass EmClass : An EmClass instance
    # @return A dict with column name as key and EmFieldType instance as value
    def _class2cols(self, emclass):
        if not isinstance(emclass, EditorialModel.classes.EmClass):
            raise ValueError("The given uid is not an EmClass uid")
        return {f.name: f.fieldtype_instance() for f in emclass.fields() if f.name not in EditorialModel.classtypes.common_fields.keys()}

    ## @brief Create object and relations tables
    # @param drop_if_exist bool : If true drop tables if exists
    def _create_default_tables(self, drop_if_exist=False):
        if_exists = 'drop' if drop_if_exist else 'nothing'
        #Object table
        tname = utils.common_tables['object']
        pk_name, pk_ftype = self._object_pk
        self._create_table(tname, pk_name, pk_ftype, engine=self.db_engine, if_exists=if_exists)
        #Adding columns
        cols = {fname: self._common_field_to_ftype(fname) for fname in EditorialModel.classtypes.common_fields}
        for fname, ftype in cols.items():
            if fname != pk_name:
                self._add_column(tname, fname, ftype, relation=False)
        #Creating triggers
        self._generate_triggers(tname, cols)
        object_tname = tname

        #Relation table
        tname = utils.common_tables['relation']
        pk_name, pk_ftype = self._relation_pk
        self._create_table(tname, pk_name, pk_ftype, engine=self.db_engine, if_exists=if_exists)
        #Adding columns
        for fname, ftype in self._relation_cols.items():
            self._add_column(tname, fname, ftype, relation=True)
        #Creating triggers
        self._generate_triggers(tname, self._relation_cols)

        # Creating foreign keys between relation and object table
        sup_cname, sub_cname = self.get_sup_and_sub_cols()

    ## @brief Returns the fieldname for superior and subordinate in relation table
    # @return a tuple (superior_name, subordinate_name)
    @classmethod
    def get_sup_and_sub_cols(cls):
        sup = None
        sub = None
        for fname, finfo in EditorialModel.classtypes.relations_common_fields.items():
            if finfo['fieldtype'] == 'leo':
                if finfo['superior']:
                    sup = fname
                else:
                    sub = fname
        return utils.column_name(sup), utils.column_name(sub)

    ## @brief Create a table with primary key
    # @param table_name str : table name
    # @param pk_name str | tuple : pk column name (give tuple for multi pk)
    # @param pk_ftype fieldtype | tuple : pk fieldtype (give a tuple for multi pk)
    # @param engine str : The engine to use with this table
    # @param charset str : The charset of this table
    # @param if_exists str : takes values in ['nothing', 'drop']
    # @param noauto_inc bool : if True forbids autoincrement on PK
    def _create_table(self, table_name, pk_name, pk_ftype, engine, charset='utf8', if_exists='nothing', noauto_inc = False):
        #Escaped table name
        etname = utils.escape_idname(table_name)
        if not isinstance(pk_name, tuple):
            pk_name = tuple([pk_name])
            pk_ftype = tuple([pk_ftype])

        if len(pk_name) != len(pk_ftype):
            raise ValueError("You have to give as many pk_name as pk_ftype")
        
        pk_instr_cols = ''
        pk_format = "{pk_name} {pk_type} {pk_specs},\n"
        for i in range(len(pk_name)):
            instr_type, pk_type, pk_specs = fieldtypes_utils.fieldtype_db_init(pk_ftype[i], noauto_inc)
            if instr_type != 'column':
                raise ValueError("Migration handler doesn't support MultiValueFieldType as primary keys")
            pk_instr_cols += pk_format.format(
                                                pk_name = utils.escape_idname(pk_name[i]),
                                                pk_type = pk_type,
                                                pk_specs = pk_specs
                                            )
        pk_instr_cols += "PRIMARY KEY("+(','.join([utils.escape_idname(pkn) for pkn in pk_name]))+')'

        if if_exists == 'drop':
            self._query("""DROP TABLE IF EXISTS {table_name};""".format(table_name=etname))

        qres = """CREATE TABLE IF NOT EXISTS {table_name} (
{pk_cols}
) ENGINE={engine} DEFAULT CHARSET={charset};""".format(
                                                        table_name = table_name,
                                                        pk_cols = pk_instr_cols,
                                                        engine = engine,
                                                        charset = charset
        )
        self._query(qres)

    ## @brief Add a column to a table
    # @param table_name str : The table name
    # @param col_name str : The columns name
    # @param col_fieldtype EmFieldype the fieldtype
    # @param relation bool | None : a flag to indicate if we add a column in a table linked with an bject or with a relation (used only when the column is MultiValueFieldType )
    # @param drop_if_exists bool : if True delete the column before re-adding it
    # @return True if the column was added else return False
    def _add_column(self, table_name, col_name, col_fieldtype, drop_if_exists=False, relation=False):
        instr, col_type, col_specs = fieldtypes_utils.fieldtype_db_init(col_fieldtype)

        if instr == 'table':
            # multivalue field. We are not going to add a column in this table
            # but in corresponding multivalue table
            self._add_column_multivalue(
                                            ref_table_name = table_name,
                                            key_infos = col_type,
                                            column_infos = (col_name, col_specs),
                                            relation = relation
                                        )
            return True

        col_name = utils.column_name(col_name)

        add_col = """ALTER TABLE {table_name}
ADD COLUMN {col_name} {col_type} {col_specs};"""

        etname = utils.escape_idname(table_name)
        ecname = utils.escape_idname(col_name)

        if instr is None:
            return True
        if instr != "column":
            raise RuntimeError("Bad implementation")

        add_col = add_col.format(
            table_name=etname,
            col_name=ecname,
            col_type=col_type,
            col_specs=col_specs,
        )
        try:
            self._query(add_col)
        except self._dbmodule.err.InternalError:
            if drop_if_exists:
                self._del_column(table_name, col_name)
                self._add_column(table_name, col_name, col_fieldtype, drop_if_exists)
            else:
                #LOG
                print("Aborded, column `%s` exists" % col_name)
                return False

        if isinstance(col_fieldtype, EditorialModel.fieldtypes.generic.ReferenceFieldType):
            # We have to create a FK !
            if col_fieldtype.reference == 'object':
                dst_table_name = utils.common_tables['object']
                dst_col_name, _ = self._object_pk
            elif col_fieldtypes.reference == 'relation':
                dst_table_name = utils.common_tables['relation']
                dst_col_name, _ = self._relation_pk
            
            fk_name = 'fk_%s-%s_%s-%s' % (
                                            table_name,
                                            col_name,
                                            dst_table_name,
                                            dst_col_name,
                                        )
                
            self._add_fk(
                            src_table_name = table_name,
                            dst_table_name = dst_table_name,
                            src_col_name = col_name,
                            dst_col_name = dst_col_name,
                            fk_name = fk_name
                        )

        return True

    ## @brief Add a column to a multivalue table
    #
    # Add a column (and create a table if not existing) for storing multivalue
    # datas. (typically i18n)
    # @param ref_table_name str : Referenced table name
    # @param key_infos tuple : tuple(key_name, key_fieldtype)
    # @param column_infos tuple : tuple(col_name, col_fieldtype)
    # @param relation bool : pass True if concern a LeRelation or False of concern a LeObject
    def _add_column_multivalue(self, ref_table_name, key_infos, column_infos, relation):
        key_name, key_ftype = key_infos
        col_name, col_ftype = column_infos
        table_name = utils.multivalue_table_name(ref_table_name, key_name)
        if relation:
            pk_infos = self._relation_pk
        else:
            pk_infos = self._object_pk
        # table creation
        self._create_table(
                            table_name = table_name,
                            pk_name = (key_name, pk_infos[0]),
                            pk_ftype = (key_ftype, pk_infos[1]),
                            engine = self.db_engine,
                            if_exists = 'nothing',
                            noauto_inc = True
        )
        # with FK
        self._add_fk(table_name, ref_table_name, pk_infos[0], pk_infos[0])
        # adding the column
        self._add_column(table_name, col_name, col_ftype)

    ## @brief Delete a multivalue column
    # @param emfield EmField : EmField instance
    # @note untested
    def _del_column_multivalue(self, emfield):
        ftype = emfield.fieldtype_instance()
        if not isinstance(ftype, MultiValueFieldType):
            raise ValueError("Except an emfield with multivalue fieldtype")
        tname = utils.object_table_name(emfield.em_class.name)
        tname = utils.multivalue_table_name(tname, ftype.keyname)
        self._del_column(tname, emfield.name)
        if len([ f for f in emfield.em_class.fields() if isinstance(f.fieldtype_instance(), MultiValueFieldType)]) == 0:
            try:
                self._query("DROP TABLE %s;" % utils.escape_idname(tname))
            except self._dbmodule.err.InternalError as expt:
                print(expt)


    ## @brief Add a foreign key
    # @param src_table_name str : The name of the table where we will add the FK
    # @param dst_table_name str : The name of the table the FK will point on
    # @param src_col_name str : The name of the concerned column in the src_table
    # @param dst_col_name str : The name of the concerned column in the dst_table
    # @param fk_name str|None : The foreign key name, if None the name will be generated (not a good idea)
    def _add_fk(self, src_table_name, dst_table_name, src_col_name, dst_col_name, fk_name=None):
        stname = utils.escape_idname(src_table_name)
        dtname = utils.escape_idname(dst_table_name)
        scname = utils.escape_idname(src_col_name)
        dcname = utils.escape_idname(dst_col_name)

        if fk_name is None:
            fk_name = utils.get_fk_name(src_table_name, dst_table_name)

        self._del_fk(src_table_name, dst_table_name, fk_name)

        self._query("""ALTER TABLE {src_table}
ADD CONSTRAINT {fk_name}
FOREIGN KEY ({src_col}) references {dst_table}({dst_col})
ON DELETE CASCADE
ON UPDATE CASCADE;""".format(
    fk_name=utils.escape_idname(fk_name),
    src_table=stname,
    src_col=scname,
    dst_table=dtname,
    dst_col=dcname
))

    ## @brief Given a source and a destination table, delete the corresponding FK
    # @param src_table_name str : The name of the table where the FK is
    # @param dst_table_name str : The name of the table the FK point on
    # @param fk_name str|None : the foreign key name, if None try to guess it
    # @warning fails silently
    def _del_fk(self, src_table_name, dst_table_name, fk_name=None):
        if fk_name is None:
            fk_name = utils.get_fk_name(src_table_name, dst_table_name)
        fk_name = utils.escape_idname(fk_name)
        try:
            self._query("""ALTER TABLE {src_table}
DROP FOREIGN KEY {fk_name}""".format(
    src_table=utils.escape_idname(src_table_name),
    fk_name=fk_name
))
        except self._dbmodule.err.InternalError:
            # If the FK don't exists we do not care
            pass

    ## @brief Generate triggers given a table_name and its columns fieldtypes
    # @param table_name str : Table name
    # @param cols_ftype dict : with col name as key and column fieldtype as value
    def _generate_triggers(self, table_name, cols_ftype):
        colval_l_upd = dict()  # param for update trigger
        colval_l_ins = dict()  # param for insert trigger

        for cname, cftype in cols_ftype.items():
            if isinstance(cftype, EditorialModel.fieldtypes.datetime.EmFieldType):
                if cftype.now_on_update:
                    colval_l_upd[cname] = 'NOW()'
                if cftype.now_on_create:
                    colval_l_ins[cname] = 'NOW()'

        self._table_trigger(table_name, 'UPDATE', colval_l_upd)
        self._table_trigger(table_name, 'INSERT', colval_l_ins)

    ## @brief Create trigger for a table
    #
    # Primarly designed to create trigger for DATETIME types
    # The method generates triggers of the form
    # <pre>
    # CREATE TRIGGER BEFORE &lt;moment&gt; ON &lt;table_name&gt;
    # FOR EACH ROW SET lt;for colname, colval in &lt;cols_val&gt;
    # NEW.lt;colname> = lt;colval&gt;,
    # lt;endfor&gt;;
    # </pre>
    # @param table_name str : The table name
    # @param moment str : can be 'update' or 'insert'
    # @param cols_val dict : Dict with column name as key and column value as value
    def _table_trigger(self, table_name, moment, cols_val):
        trigger_name = utils.escape_idname("%s_%s_trig" % (table_name, moment))
        #Try to delete the trigger
        drop_trig = """DROP TRIGGER IF EXISTS {trigger_name};""".format(trigger_name=trigger_name)
        self._query(drop_trig)

        col_val_l = ', '.join(["NEW.%s = %s" % (utils.escape_idname(utils.column_name(cname)), cval)for cname, cval in cols_val.items()])
        #Create a trigger if needed
        if len(col_val_l) > 0:
            trig_q = """CREATE TRIGGER {trigger_name} BEFORE {moment} ON {table_name}
FOR EACH ROW SET {col_val_list};""".format(
    trigger_name=trigger_name,
    table_name=utils.escape_idname(table_name),
    moment=moment, col_val_list=col_val_l
)
            self._query(trig_q)

    ## @brief Delete all table created by the MH
    # @param model Model : the Editorial model
    def __purge_db(self, model):
        for uid in [
                    field
                    for field in model.components('EmField')
                    if isinstance(field.fieldtype_instance(), MultiValueFieldType)
        ]:
            self._del_column_multivalue(field)

        for uid in [c.uid for c in model.components('EmClass')]:
            try:
                self.delete_emclass_table(model, uid)
            except self._dbmodule.err.InternalError as expt:
                print(expt)

        for tname in [utils.r2t_table_name(f.em_class.name, model.component(f.rel_to_type_id).name) for f in model.components('EmField') if f.fieldtype == 'rel2type']:
            try:
                self._query("DROP TABLE %s;" % tname)
            except self._dbmodule.err.InternalError as expt:
                print(expt)

        for tname in [utils.common_tables['relation'], utils.common_tables['relation']]:
            try:
                self._query("DROP TABLE %s;" % tname)
            except self._dbmodule.err.InternalError as expt:
                print(expt)

    ## @brief Return primary key name & fieldtype for relation or object
    @classmethod
    def extract_pk(cls, common_fields):
        for fname, finfo in common_fields.items():
            if finfo['fieldtype'] == 'pk':
                fto = EditorialModel.fieldtypes.generic.GenericFieldType.from_name('pk')
                finfo_cp = copy.copy(finfo)
                del(finfo_cp['fieldtype'])
                return (utils.column_name(fname), fto(**finfo_cp))
        raise RuntimeError("No primary key found in common fields : %s" % common_fields)

    ## @brief Exec a query
    # @param query str : SQL query
    def _query(self, query):
        if self.debug:
            print(query + "\n")
        if not self.dryrun:
            with self.db_conn.cursor() as cur:
                cur.execute(query)
        self.db_conn.commit()  # autocommit

    ## @brief Given a common field name return an EmFieldType instance
    # @param cls
    # @param cname str : Common field name
    # @return An EmFieldType instance
    @classmethod
    def _common_field_to_ftype(cls, cname):
        fta = copy.copy(EditorialModel.classtypes.common_fields[cname])
        fto = EditorialModel.fieldtypes.generic.GenericFieldType.from_name(fta['fieldtype'])
        del fta['fieldtype']
        return fto(**fta)

    ## @brief Returns a tuple (pkname, pk_ftype)
    @property
    def _object_pk(self):
        return self.extract_pk(EditorialModel.classtypes.common_fields)

    ## @brief Returns a tuple (rel_pkname, rel_ftype)
    @property
    def _relation_pk(self):
        return self.extract_pk(EditorialModel.classtypes.relations_common_fields)

    ## @brief Returns a dict { colname:fieldtype } of relation table columns
    @property
    def _relation_cols(self):
        res = dict()
        for fieldname, fieldinfo in EditorialModel.classtypes.relations_common_fields.items():
            finfo = copy.copy(fieldinfo)
            fieldtype_name = finfo['fieldtype']
            del(finfo['fieldtype'])
            res[fieldname] = EditorialModel.fieldtypes.generic.GenericFieldType.from_name(fieldtype_name)(**finfo)
        return res
