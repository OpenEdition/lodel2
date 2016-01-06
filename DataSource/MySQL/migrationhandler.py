# -*- coding: utf-8 -*-

import copy
import pymysql

import EditorialModel
import EditorialModel.classtypes
import EditorialModel.fieldtypes
import EditorialModel.fieldtypes.generic

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
# - EmClass deletion (untested)
# - EmField creation
# - EmField deletion (untested)
# - rel2type attribute creation
# - rel2type attribute deletion (unstested)
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
    # @param host str : The db host
    # @param user str : The db user
    # @param password str : The db password
    # @param db str : The db name
    def __init__(self, host, user, passwd, db, module=pymysql, db_engine='InnoDB', foreign_keys=True, debug=False, dryrun=False, drop_if_exists=False):
        self._dbmodule = module
        #Connect to MySQL
        self.db = self._dbmodule.connect(host=host, user=user, passwd=passwd, db=db)
        self.debug = debug
        self.dryrun = dryrun
        self.db_engine = db_engine
        self.foreign_keys = foreign_keys if db_engine == 'InnoDB' else False
        self.drop_if_exists = drop_if_exists
        #Create default tables
        self._create_default_tables(self.drop_if_exists)

    ## @brief Delete all table created by the MH
    # @param model Model : the Editorial model
    def __purge_db(self, model):
        for uid in [c.uid for c in model.components('EmClass')]:
            try:
                self.delete_emclass_table(model, uid)
            except self._dbmodule.err.InternalError as e:
                print(e)

        for tname in [MySQL.get_r2t2table_name(f.em_class.name, model.component(f.rel_to_type_id).name) for f in model.components('EmField') if f.fieldtype == 'rel2type']:
            try:
                self._query("DROP TABLE %s;" % tname)
            except self._dbmodule.err.InternalError as e:
                print(e)

        for tname in [MySQL.relations_table_name, MySQL.objects_table_name]:
            try:
                self._query("DROP TABLE %s;" % tname)
            except self._dbmodule.err.InternalError as e:
                print(e)

    ## @brief Modify the db given an EM change
    # @param em model : The EditorialModel.model object to provide the global context
    # @param uid int : The uid of the change EmComponent
    # @param initial_state dict | None : dict with field name as key and field value as value. Representing the original state. None mean creation of a new component.
    # @param new_state dict | None : dict with field name as key and field value as value. Representing the new state. None mean component deletion
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
                        self.del_col_from_emfield(em, uid)
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

    ## @brief Exec a query
    # @param query str : SQL query
    def _query(self, query):
        if self.debug:
            print(query + "\n")
        if not self.dryrun:
            with self.db.cursor() as cur:
                cur.execute(query)
        self.db.commit()  # autocommit

    ## @brief Add a relationnal field
    # Add a rel2type attribute
    # @note this function handles the table creation
    # @param em Model : EditorialModel.model.Model instance
    # @param rfuid int : Relationnal field uid
    def add_relationnal_field(self, em, rfuid):
        emfield = em.component(rfuid)
        if not isinstance(emfield, EditorialModel.fields.EmField):
            raise ValueError("The given uid is not an EmField uid")

        r2tf = em.component(emfield.rel_field_id)
        tname = self._r2t2table_name(em, r2tf)
        pkname, pkftype = self._relation_pk

        #If not exists create a relational table
        self._create_table(tname, pkname, pkftype, self.db_engine, if_exists='nothing')
        #Add a foreign key if wanted
        if self.foreign_keys:
            self._add_fk(tname, utils.common_tables['relation'], pkname, pkname)
        #Add the column
        self._add_column(tname, emfield.name, emfield.fieldtype_instance())
        #Update table triggers
        self._generate_triggers(tname, self._r2type2cols(em, r2tf))

    ## @brief Delete a rel2type attribute
    #
    # Delete a rel2type attribute
    # @note this method handles the table deletion
    # @param em Model : EditorialModel.model.Model instance
    # @param rfuid int : Relationnal field uid
    def del_relationnal_field(self, em, rfuid):
        emfield = em.component(rfuid)
        if not isinstance(emfield, EditorialModel.fields.EmField):
            raise ValueError("The given uid is not an EmField uid")

        r2tf = em.component(emfield.rel_field_id)
        tname = self._r2t2table_name(em, r2tf)

        if len(self._r2type2cols(em, r2tf)) == 1:
            #The table can be deleted (no more attribute for this rel2type)
            self._query("""DROP TABLE {table_name}""".format(table_name=tname))
        else:
            self._del_column(tname, emfield.name)
            #Update table triggers
            self._generate_triggers(tname, self._r2type2cols(em, r2tf))

    ## @brief Given an EmField uid add a column to the corresponding table
    # @param em Model : A Model instance
    # @param uid int : An EmField uid
    def add_col_from_emfield(self, em, uid):
        emfield = em.component(uid)
        if not isinstance(emfield, EditorialModel.fields.EmField):
            raise ValueError("The given uid is not an EmField uid")

        emclass = emfield.em_class
        tname = self._emclass2table_name(emclass)
        self._add_column(tname, emfield.name, emfield.fieldtype_instance())
        # Refresh the table triggers
        cols_l = self._class2cols(emclass)
        self._generate_triggers(tname, cols_l)

    ## @brief Given a class uid create the coressponding table
    # @param em Model : A Model instance
    # @param uid int : An EmField uid
    def create_emclass_table(self, em, uid, engine):
        emclass = em.component(uid)
        if not isinstance(emclass, EditorialModel.classes.EmClass):
            raise ValueError("The given uid is not an EmClass uid")
        pkname, pktype = self._common_field_pk
        table_name = self._emclass2table_name(emclass)
        self._create_table(table_name, pkname, pktype, engine=engine)

        if self.foreign_keys:
            self._add_fk(table_name, utils.common_tables['object'], pkname, pkname)

    ## @brief Given an EmClass uid delete the corresponding table
    # @param em Model : A Model instance
    # @param uid int : An EmField uid
    def delete_emclass_table(self, em, uid):
        emclass = em.component(uid)
        if not isinstance(emclass, EditorialModel.classes.EmClass):
            raise ValueError("The give uid is not an EmClass uid")
        tname = self._emclass2table_name(emclass)
        # Delete the table triggers to prevent errors
        self._generate_triggers(tname, dict())

        tname = utils.escape_idname(tname)

        self._query("""DROP TABLE {table_name};""".format(table_name=tname))

    ## @brief Given an EmField delete the corresponding column
    # @param em Model : an @ref EditorialModel.model.Model instance
    # @param uid int : an EmField uid
    def delete_col_from_emfield(self, em, uid):
        emfield = em.component(uid)
        if not isinstance(emfield, EditorialModel.fields.EmField):
            raise ValueError("The given uid is not an EmField uid")

        emclass = emfield.em_class
        tname = self._emclass2table_name(emclass)
        # Delete the table triggers to prevent errors
        self._generate_triggers(tname, dict())

        self._del_column(tname, emfield.name)
        # Refresh the table triggers
        cols_ls = self._class2cols(emclass)
        self._generate_triggers(tname, cols_l)

    ## @brief Delete a column from a table
    # @param tname str : The table name
    # @param fname str : The column name
    def _del_column(self, tname, fname):
        tname = utils.escape_idname(tname)
        fname = utils.escape_idname(fname)

        self._query("""ALTER TABLE {table_name} DROP COLUMN {col_name};""".format(table_name=tname, col_name=fname))

    ## @brief Construct a table name given an EmClass instance
    # @param emclass EmClass : An EmClass instance
    # @return a table name
    def _emclass2table_name(self, emclass):
        return utils.object_table_name(emclass.name)

    ## @brief Construct a table name given a rela2type EmField instance
    # @param em Model : A Model instance
    # @param emfield EmField : An EmField instance
    # @return a table name
    def _r2t2table_name(self, em, emfield):
        emclass = emfield.em_class
        emtype = em.component(emfield.rel_to_type_id)
        return utils.r2t_table_name(emclass.name, emtype.name)

    ## @brief Generate a columns_fieldtype dict given a rel2type EmField
    # @param em Model : an @ref EditorialModel.model.Model instance
    # @param emfield EmField : and @ref EditorialModel.fields.EmField instance
    def _r2type2cols(self, em, emfield):
        return {f.name: f.fieldtype_instance() for f in em.components('EmField') if f.rel_field_id == emfield.uid}

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
        pk_name, pk_ftype = self._common_field_pk
        self._create_table(tname, pk_name, pk_ftype, engine=self.db_engine, if_exists=if_exists)
        #Adding columns
        cols = {fname: self._common_field_to_ftype(fname) for fname in EditorialModel.classtypes.common_fields}
        for fname, ftype in cols.items():
            if fname != pk_name:
                self._add_column(tname, fname, ftype)
        #Creating triggers
        self._generate_triggers(tname, cols)

        #Relation table
        tname = utils.common_tables['relation']
        pk_name, pk_ftype = self._relation_pk
        self._create_table(tname, pk_name, pk_ftype, engine=self.db_engine, if_exists=if_exists)
        #Adding columns
        for fname, ftype in self._relation_cols.items():
            self._add_column(tname, fname, ftype)
        #Creating triggers
        self._generate_triggers(tname, self._relation_cols)

    ## @return true if the name changes
    def _name_change(self, initial_state, new_state):
        return 'name' in initial_state and initial_state['name'] != new_state['name']

    ## @brief Create a table with primary key
    # @param table_name str : table name
    # @param pk_name str : pk column name
    # @param pk_specs str : see @ref _field_to_sql()
    # @param engine str : The engine to use with this table
    # @param charset str : The charset of this table
    # @param if_exist str : takes values in ['nothing', 'drop']
    def _create_table(self, table_name, pk_name, pk_ftype, engine, charset='utf8', if_exists='nothing'):
        #Escaped table name
        etname = utils.escape_idname(table_name)
        pk_type = self._field_to_type(pk_ftype)
        pk_specs = self._field_to_specs(pk_ftype)

        if if_exists == 'drop':
            self._query("""DROP TABLE IF EXISTS {table_name};""".format(table_name=etname))
            qres = """
CREATE TABLE {table_name} (
{pk_name} {pk_type} {pk_specs},
PRIMARY KEY({pk_name})
) ENGINE={engine} DEFAULT CHARSET={charset};"""
        elif if_exists == 'nothing':
            qres = """CREATE TABLE IF NOT EXISTS {table_name} (
{pk_name} {pk_type} {pk_specs},
PRIMARY KEY({pk_name})
) ENGINE={engine} DEFAULT CHARSET={charset};"""
        else:
            raise ValueError("Unexpected value for argument if_exists '%s'." % if_exists)

        self._query(qres.format(
            table_name=utils.escape_idname(table_name),
            pk_name=utils.escape_idname(pk_name),
            pk_type=pk_type,
            pk_specs=pk_specs,
            engine=engine,
            charset=charset
        ))

    ## @brief Add a column to a table
    # @param table_name str : The table name
    # @param col_name str : The columns name
    # @param col_fieldtype EmFieldype the fieldtype
    def _add_column(self, table_name, col_name, col_fieldtype, drop_if_exists=False):

        col_name = utils.column_name(col_name)

        add_col = """ALTER TABLE {table_name}
ADD COLUMN {col_name} {col_type} {col_specs};"""

        etname = utils.escape_idname(table_name)
        ecname = utils.escape_idname(col_name)

        add_col = add_col.format(
            table_name=etname,
            col_name=ecname,
            col_type=self._field_to_type(col_fieldtype),
            col_specs=self._field_to_specs(col_fieldtype),
        )
        try:
            self._query(add_col)
        except self._dbmodule.err.InternalError as e:
            if drop_if_exists:
                self._del_column(table_name, col_name)
                self._add_column(table_name, col_name, col_fieldtype, drop_if_exists)
            else:
                #LOG
                print("Aborded, column `%s` exists" % col_name)

    ## @brief Add a foreign key
    # @param src_table_name str : The name of the table where we will add the FK
    # @param dst_table_name str : The name of the table the FK will point on
    # @param src_col_name str : The name of the concerned column in the src_table
    # @param dst_col_name str : The name of the concerned column in the dst_table
    def _add_fk(self, src_table_name, dst_table_name, src_col_name, dst_col_name):
        stname = utils.escape_idname(src_table_name)
        dtname = utils.escape_idname(dst_table_name)
        scname = utils.escape_idname(src_col_name)
        dcname = utils.escape_idname(dst_col_name)

        fk_name = utils.get_fk_name(src_table_name, dst_table_name)

        self._del_fk(src_table_name, dst_table_name)

        self._query("""ALTER TABLE {src_table}
ADD CONSTRAINT {fk_name}
FOREIGN KEY ({src_col}) references {dst_table}({dst_col});""".format(
            fk_name=utils.escape_idname(fk_name),
            src_table=stname,
            src_col=scname,
            dst_table=dtname,
            dst_col=dcname
        ))

    ## @brief Given a source and a destination table, delete the corresponding FK
    # @param src_table_name str : The name of the table where the FK is
    # @param dst_table_name str : The name of the table the FK point on
    # @warning fails silently
    def _del_fk(self, src_table_name, dst_table_name):
        try:
            self._query("""ALTER TABLE {src_table}
DROP FOREIGN KEY {fk_name}""".format(
                src_table=utils.escape_idname(src_table_name),
                fk_name=utils.escape_idname(utils.get_fk_name(src_table_name, dst_table_name))
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
            if cftype.ftype == 'datetime':
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
    #
    # CREATE TRIGGER BEFORE <moment> ON <table_name>
    # FOR EACH ROW SET <for colname, colval in cols_val>
    # NEW.<colname> = <colval>,
    # <endfor>;
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

    ## @brief Identifier escaping
    # @param idname str : An SQL identifier
    #def _idname_escape(self, idname):
    #    if '`' in idname:
    #        raise ValueError("Invalid name : '%s'"%idname)
    #    return '`%s`'%idname

    ## @brief Returns column specs from fieldtype
    # @param emfieldtype EmFieldType : An EmFieldType insance
    # @todo escape default value
    def _field_to_specs(self, emfieldtype):
        colspec = ''
        if not emfieldtype.nullable:
            colspec = 'NOT NULL'
        if hasattr(emfieldtype, 'default'):
            colspec += ' DEFAULT '
            if emfieldtype.default is None:
                colspec += 'NULL '
            else:
                colspec += emfieldtype.default  # ESCAPE VALUE HERE !!!!

        if emfieldtype.name == 'pk':
            colspec += ' AUTO_INCREMENT'

        return colspec

    ## @brief Given a fieldtype return a MySQL type specifier
    # @param emfieldtype EmFieldType : A fieldtype
    # @return the corresponding MySQL type
    def _field_to_type(self, emfieldtype):
        ftype = emfieldtype.ftype

        if ftype == 'char' or ftype == 'str':
            res = "VARCHAR(%d)" % emfieldtype.max_length
        elif ftype == 'text':
            res = "TEXT"
        elif ftype == 'datetime':
            res = "DATETIME"
            # client side workaround for only one column with CURRENT_TIMESTAMP : giving NULL to timestamp that don't allows NULL
            # cf. https://dev.mysql.com/doc/refman/5.0/en/timestamp-initialization.html#idm139961275230400
            # The solution for the migration handler is to create triggers :
            # CREATE TRIGGER trigger_name BEFORE INSERT ON `my_super_table`
            # FOR EACH ROW SET NEW.my_date_column = NOW();
            # and
            # CREATE TRIGGER trigger_name BEFORE UPDATE ON

        elif ftype == 'bool':
            res = "BOOL"
        elif ftype == 'int':
            res = "INT"
        elif ftype == 'rel2type':
            res = "INT"
        elif ftype == 'leobject':
            res = "INT"
        else:
            raise ValueError("Unsuported fieldtype ftype : %s" % ftype)

        return res

    ## @brief Return primary key name & fieldtype for relation or object
    @classmethod
    def extract_pk(cls, common_fields):
        for fname, finfo in common_fields.items():
            if finfo['fieldtype'] == 'pk':
                fto = EditorialModel.fieldtypes.generic.GenericFieldType.from_name('pk')
                finfo_cp = copy.copy(finfo)
                del(finfo_cp['fieldtype'])
                return (utils.column_name(fname), fto(**finfo_cp))
        raise RuntimeError("No primary key found in common fields : %s"%common_fields)

    ## @brief Returns a tuple (pkname, pk_ftype)
    @property
    def _common_field_pk(self):
        return self.extract_pk(EditorialModel.classtypes.common_fields)

    ## @brief Returns a tuple (rel_pkname, rel_ftype)
    @property
    def _relation_pk(self):
        return self.extract_pk(EditorialModel.classtypes.relations_common_fields)

    ## @brief Returns a dict { colname:fieldtype } of relation table columns
    @property
    def _relation_cols(self):
        from_name = EditorialModel.fieldtypes.generic.GenericFieldType.from_name
        res = dict()
        for fieldname, fieldinfo in EditorialModel.classtypes.relations_common_fields.items():
            finfo = copy.copy(fieldinfo)
            fieldtype_name = finfo['fieldtype']
            del(finfo['fieldtype'])
            res[fieldname] = EditorialModel.fieldtypes.generic.GenericFieldType.from_name(fieldtype_name)(**finfo)
        return res

    ## @brief Given a common field name return an EmFieldType instance
    # @param cname str : Common field name
    # @return An EmFieldType instance
    @classmethod
    def _common_field_to_ftype(cls, cname):
        fta = copy.copy(EditorialModel.classtypes.common_fields[cname])
        fto = EditorialModel.fieldtypes.generic.GenericFieldType.from_name(fta['fieldtype'])
        del fta['fieldtype']
        return fto(**fta)
