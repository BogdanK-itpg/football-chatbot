import importlib
import os
import sqlite3
import tempfile
from unittest import mock

from test_support import BasePatchedTestCase


class TestDbModule(BasePatchedTestCase):
    def setUp(self):
        self.db = importlib.import_module('db')

    def test_initialize_database_creates_new_db_and_seeds(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = os.path.join(tmp, 'football.db')
            schema = os.path.join(tmp, 'schema.sql')
            seed = os.path.join(tmp, 'seed_demo.sql')
            migration = os.path.join(tmp, 'migration.sql')
            with open(schema, 'w', encoding='utf-8') as f:
                f.write('CREATE TABLE clubs (id INTEGER PRIMARY KEY, name TEXT);')
            with open(seed, 'w', encoding='utf-8') as f:
                f.write("INSERT INTO clubs (id, name) VALUES (1, 'Demo');")
            with open(migration, 'w', encoding='utf-8') as f:
                f.write('')

            with mock.patch.object(self.db, 'DB_PATH', db_path), \
                 mock.patch.object(self.db, 'SCHEMA_PATH', schema), \
                 mock.patch.object(self.db, 'MIGRATION_PATH', migration):
                self.db.initialize_database()

            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute('SELECT COUNT(*) FROM clubs')
            self.assertEqual(cur.fetchone()[0], 1)
            conn.close()

    def test_initialize_database_runs_migration_when_flag_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = os.path.join(tmp, 'football.db')
            migration = os.path.join(tmp, 'migration.sql')
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute('CREATE TABLE base (id INTEGER PRIMARY KEY)')
            conn.commit()
            conn.close()
            with open(migration, 'w', encoding='utf-8') as f:
                f.write('CREATE TABLE migrated (id INTEGER);')

            with mock.patch.object(self.db, 'DB_PATH', db_path), \
                 mock.patch.object(self.db, 'MIGRATION_PATH', migration):
                self.db.initialize_database()

            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='migrated'")
            self.assertIsNotNone(cur.fetchone())
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='_migration_done'")
            self.assertIsNotNone(cur.fetchone())
            conn.close()

    def test_run_migration_ignores_statement_errors(self):
        conn = sqlite3.connect(':memory:')
        cur = conn.cursor()
        with tempfile.TemporaryDirectory() as tmp:
            migration = os.path.join(tmp, 'migration.sql')
            with open(migration, 'w', encoding='utf-8') as f:
                f.write('CREATE TABLE x (id INTEGER);CREATE TABLE x (id INTEGER);')
            with mock.patch.object(self.db, 'MIGRATION_PATH', migration):
                self.db._run_migration(conn, cur)
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='_migration_done'")
        self.assertIsNotNone(cur.fetchone())
        conn.close()

    def test_insert_sample_data_raises_when_seed_missing(self):
        conn = sqlite3.connect(':memory:')
        cur = conn.cursor()
        with tempfile.TemporaryDirectory() as tmp:
            fake_schema = os.path.join(tmp, 'schema.sql')
            with open(fake_schema, 'w', encoding='utf-8') as f:
                f.write('')
            with mock.patch.object(self.db, 'SCHEMA_PATH', fake_schema):
                with self.assertRaises(FileNotFoundError):
                    self.db._insert_sample_data(conn, cur)
        conn.close()

    def test_get_connection_handles_pragma_failure(self):
        real_connect = sqlite3.connect

        class ConnWrapper:
            def __init__(self, inner):
                self.inner = inner
                self.row_factory = None

            def execute(self, *_args, **_kwargs):
                raise RuntimeError('pragma fail')

            def __getattr__(self, name):
                return getattr(self.inner, name)

        with tempfile.TemporaryDirectory() as tmp:
            db_path = os.path.join(tmp, 'football.db')
            schema = os.path.join(tmp, 'schema.sql')
            seed = os.path.join(tmp, 'seed_demo.sql')
            migration = os.path.join(tmp, 'migration.sql')
            with open(schema, 'w', encoding='utf-8') as f:
                f.write('CREATE TABLE clubs (id INTEGER PRIMARY KEY, name TEXT);')
            with open(seed, 'w', encoding='utf-8') as f:
                f.write("INSERT INTO clubs (id, name) VALUES (1, 'Demo');")
            with open(migration, 'w', encoding='utf-8') as f:
                f.write('')

            def fake_connect(path):
                return ConnWrapper(real_connect(path))

            with mock.patch.object(self.db, 'DB_PATH', db_path), \
                 mock.patch.object(self.db, 'SCHEMA_PATH', schema), \
                 mock.patch.object(self.db, 'MIGRATION_PATH', migration), \
                 mock.patch('db.sqlite3.connect', side_effect=fake_connect):
                conn = self.db.get_connection()
                self.assertIsNotNone(conn)
                conn.close()

    def test_get_connection_handles_exception(self):
        with mock.patch('db.initialize_database', side_effect=RuntimeError('boom')):
            self.assertIsNone(self.db.get_connection())

    def test_execute_query_fetch_paths_and_error(self):
        fake_conn = mock.Mock()
        fake_cursor = fake_conn.cursor.return_value
        fake_cursor.fetchall.return_value = [{'count': 1}]
        with mock.patch('db.get_connection', return_value=fake_conn):
            self.assertEqual(self.db.execute_query('SELECT 1', fetch=True), [{'count': 1}])
        fake_cursor.fetchall.return_value = []
        with mock.patch('db.get_connection', return_value=fake_conn):
            self.assertIsNone(self.db.execute_query('SELECT 1', fetch=True))
        with mock.patch('db.get_connection', return_value=fake_conn):
            self.assertTrue(self.db.execute_query('UPDATE x SET y=1'))
        fake_cursor.execute.side_effect = sqlite3.Error('bad')
        with mock.patch('db.get_connection', return_value=fake_conn):
            self.assertIsNone(self.db.execute_query('BROKEN'))

    def test_execute_variants_fetch_helpers_and_tx_helpers(self):
        own_conn = mock.Mock()
        own_cursor = own_conn.cursor.return_value
        own_cursor.lastrowid = 5
        with mock.patch('db.get_connection', return_value=own_conn):
            self.assertEqual(self.db.execute('INSERT INTO x VALUES (1)'), 5)
        own_cursor.lastrowid = 0
        with mock.patch('db.get_connection', return_value=own_conn):
            self.assertTrue(self.db.execute('UPDATE x SET y=1'))
        own_cursor.execute.side_effect = sqlite3.Error('fail')
        with mock.patch('db.get_connection', return_value=own_conn):
            self.assertIsNone(self.db.execute('BROKEN'))
        own_cursor.execute.side_effect = None

        passed_conn = mock.Mock()
        passed_cursor = passed_conn.cursor.return_value
        passed_cursor.lastrowid = 3
        self.assertEqual(self.db.execute('INSERT', conn=passed_conn), 3)
        passed_cursor.lastrowid = 0
        self.assertTrue(self.db.execute('UPDATE', conn=passed_conn))
        passed_cursor.execute.side_effect = sqlite3.Error('bad')
        self.assertIsNone(self.db.execute('BROKEN', conn=passed_conn))

        fetch_conn = mock.Mock()
        fetch_cursor = fetch_conn.cursor.return_value
        fetch_cursor.fetchall.return_value = [1, 2]
        with mock.patch('db.get_connection', return_value=fetch_conn):
            self.assertEqual(self.db.fetch_all('SELECT * FROM x'), [1, 2])
        fetch_cursor.execute.side_effect = sqlite3.Error('oops')
        with mock.patch('db.get_connection', return_value=fetch_conn):
            self.assertEqual(self.db.fetch_all('BROKEN'), [])
        with mock.patch('db.get_connection', return_value=None):
            self.assertEqual(self.db.fetch_all('SELECT'), [])
        with mock.patch('db.fetch_all', return_value=[{'id': 1}]):
            self.assertEqual(self.db.fetch_one('SELECT'), {'id': 1})
        with mock.patch('db.fetch_all', return_value=[]):
            self.assertIsNone(self.db.fetch_one('SELECT'))

        conn = mock.Mock()
        self.db.commit(conn)
        conn.commit.assert_called_once()
        self.db.rollback(conn)
        conn.rollback.assert_called_once()
        self.db.commit(None)
        self.db.rollback(None)
