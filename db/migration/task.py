from sqlalchemy.engine.reflection import Inspector
from termcolor import colored
from util import logger
from util.config import config
from search import ElasticService
from search.model import CircleDocument, UserDocument
from db import engine
from db.model import (
    Comment, Circle, Forgot, History, Intention, Invitation,
    Post, PostRestriction, SessionToken, User
)


class Migration:
    def __init__(self):
        # table list to create
        self._tables = [
            Comment,
            Circle,
            Forgot,
            History,
            Intention,
            Invitation,
            Post,
            PostRestriction,
            SessionToken,
            User,
        ]

        self._indices = [
            CircleDocument,
            UserDocument,
        ]

        # sqlalchemy reflector
        self._inspector = Inspector.from_engine(engine)

    def _create_table(self, table):
        """
        Create table according to given definition

        param db.Base table: table definition
        """
        table_name = table.__tablename__

        tc = colored(table_name, 'green', attrs=['bold'])
        logger.info(tc + ' table is creating')

        try:
            # create table
            table.__table__.create(engine)
        except Exception as e:
            m = tc + ' table could not created. Please check bellow'
            logger.error(m)
            logger.exception(e)

    def _alter_table(self, table):
        """
        Alter table according given definition

        There are only 2 schema update type,
            drop: drop table and create with new definition
            upadte: update schema definition

        param db.Base table: table definition
        """
        table_name = table.__tablename__

        # apply schema drop-create
        if config.db.migration == 'drop':
            tc = colored(table_name, 'red', attrs=['bold'])
            logger.info(tc + ' table is deleting')

            # drop table
            table.__table__.drop(engine)

            tc = colored(table_name, 'green', attrs=['bold'])
            logger.info(tc + ' table is creating again')

            # create table
            table.__table__.create(engine)
            return

        # apply schema update
        if config.db.migration == 'update':
            real_cols = self._inspector.get_columns(table_name)
            orm_cols = table.__table__.columns

            # check that do we need to create new column according
            # or ORM definition
            for oc in orm_cols:
                exists = False

                # check table has orm columns in the db
                for rc in real_cols:
                    if oc.name == rc.get('name'):
                        exists = True
                        break

                # create column from table
                if not exists:
                    tc = colored(table_name, 'yellow', attrs=['bold'])
                    cc = colored(oc.name, 'green', attrs=['bold'])
                    logger.info(f'{cc} adding to table {tc}')

                    sql_type = str(oc.type)
                    null = 'DEFAULT NULL' if oc.nullable else 'NOT NULL'
                    f = 'ALTER TABLE {0} ADD COLUMN {1} {2} {3}'
                    cq = f.format(table_name, oc.name, sql_type, null)

                    # create new column
                    with engine.connect() as conn:
                        conn.execute(cq)

                    # create index if column has index
                    if oc.index:
                        index = f'ix_{table_name}_{oc.name}'
                        unique = 'UNIQUE' if oc.unique else ''

                        tc = colored(table_name, 'yellow', attrs=['bold'])
                        cc = colored(oc.name, 'green', attrs=['bold'])
                        logger.info(f'index {index} adding to table {tc}')

                        f = 'CREATE INDEX {0} {1} ON {2} ({3})'
                        iq = f.format(unique, index, table_name, oc.name)

                        # create new index according to column definition
                        with engine.connect() as conn:
                            conn.execute(iq)

            # check that do we need to delete column according
            # or table definition
            for rc in real_cols:
                delete = True

                # check table has real columns in the ORM definition
                for oc in orm_cols:
                    if oc.name == rc.get('name'):
                        delete = False
                        break

                # delete column from table
                if delete:
                    tc = colored(table_name, 'yellow', attrs=['bold'])
                    cc = colored(rc.get('name'), 'red', attrs=['bold'])

                    column_name = rc.get('name')
                    index = f'ix_{table_name}_{column_name}'
                    indices = self._inspector.get_indexes(table_name)
                    for idc in indices:
                        if index != idc.get('name'):
                            continue

                        logger.info(f'Index {index} deleting from table {tc}')

                        cq = f'DROP INDEX {index}'

                        # drop index
                        with engine.connect() as conn:
                            conn.execute(cq)

                    logger.info(f'{cc} deleting from table {tc}')

                    f = 'ALTER TABLE {0} DROP COLUMN {1}'
                    cq = f.format(table_name, column_name)

                    # drop column
                    with engine.connect() as conn:
                        conn.execute(cq)
            return

        raise Exception(f'Invalid migration type {config.db.migration}')

    def migrate(self):
        """
        Migrate tables according to table definitions
        """
        # list all of created tables
        created_tables = self._inspector.get_table_names()

        for table in self._tables:
            table_name = table.__tablename__

            if table_name in created_tables:
                # update table schema
                self._alter_table(table)
            else:
                # create table
                self._create_table(table)

        es = ElasticService()

        for index in self._indices:
            # ignore index creation if index exists
            if es.client.indices.exists(index.Index.name):
                continue

            # create index
            index.init(using=es.client)
