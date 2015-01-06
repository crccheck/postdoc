# -*- coding: utf-8 -*-

import os
try:
    # for python 2.6 compatibility
    import unittest2 as unittest
except ImportError:
    import unittest

import mock

import postdoc


class ConnectBitsTest(unittest.TestCase):
    def test_pg_connect_bits_trivial_case(self):
        meta = type('mock', (object, ),
                {'username': '', 'hostname': '', 'port': ''})
        result = postdoc.pg_connect_bits(meta)
        self.assertEqual(result, [])

    def test_pg_connect_bits_works(self):
        meta = type('mock', (object, ),
            {'scheme': 'postgres', 'username': '1', 'hostname': '2', 'port': 3})
        result = postdoc.pg_connect_bits(meta)
        self.assertEqual(result, ['-U', '1', '-h', '2', '-p', '3'])
        result = postdoc.connect_bits(meta)
        self.assertEqual(result, ['-U', '1', '-h', '2', '-p', '3'])

    def test_mysql_connect_bits_trivial_case(self):
        meta = type('mock', (object, ),
                {'username': '', 'password': '', 'hostname': '', 'port': ''})
        result = postdoc.mysql_connect_bits(meta)
        self.assertEqual(result, [])

    def test_mysql_connect_bits_works(self):
        meta = type('mock', (object, ),
            {'scheme': 'mysql', 'username': 'u', 'password': 'p',
            'hostname': 'h', 'port': '3306'})
        result = postdoc.mysql_connect_bits(meta)
        self.assertEqual(result, ['-u', 'u', '-pp', '-h', 'h', '-P', '3306'])
        result = postdoc.connect_bits(meta)
        self.assertEqual(result, ['-u', 'u', '-pp', '-h', 'h', '-P', '3306'])

    def test_connect_bits_supported_schemas(self):
        meta = type('mock', (object, ),
            {'username': '', 'password': '', 'hostname': 'h', 'port': ''})

        # assert defaults to postgres
        self.assertTrue(postdoc.connect_bits(meta))
        meta.scheme = 'mysql'
        self.assertTrue(postdoc.connect_bits(meta))
        meta.scheme = 'postgres'
        self.assertTrue(postdoc.connect_bits(meta))
        meta.scheme = 'postgresql'
        self.assertTrue(postdoc.connect_bits(meta))
        meta.scheme = 'postgis'
        self.assertTrue(postdoc.connect_bits(meta))
        meta.scheme = 'foo'
        self.assertRaises(KeyError, postdoc.connect_bits, meta)


class PHDTest(unittest.TestCase):
    def test_get_uri(self):
        with mock.patch('postdoc.os') as mock_os:
            mock_os.environ = {
                'DATABASE_URL': 'foo',
                'FATTYBASE_URL': 'bar',
            }
            self.assertEqual(postdoc.get_uri().path, 'foo')
            self.assertEqual(postdoc.get_uri('FATTYBASE_URL').path, 'bar')

    def test_get_command_assembles_bits_in_right_order(self):
        meta = type('mock', (object, ),
                {'username': '', 'hostname': '', 'port': '', 'password': '',
                'path': '/database'})
        with mock.patch('postdoc.pg_connect_bits') as mock_bits:
            mock_bits.return_value = ['lol']
            self.assertEqual(postdoc.get_command('foo', meta),
                    ['foo', 'lol', 'database'])

    def test_get_command_ignores_password(self):
        meta = type('mock', (object, ),
                {'username': '', 'hostname': '', 'port': '', 'password': 'oops',
                'path': '/database'})
        with mock.patch('postdoc.pg_connect_bits') as mock_bits:
            mock_bits.return_value = ['rofl']
            self.assertEqual(postdoc.get_command('bar', meta),
                    ['bar', 'rofl', 'database'])

    def test_get_commands_can_ignore_database_name(self):
        meta = type('mock', (object, ),
            {'scheme': 'mysql', 'username': 'u', 'hostname': 'h', 'port': '',
            'password': 'oops', 'path': '/database'})
        result = postdoc.get_command('mysqladmin', meta)
        # assert database name is not an argument
        self.assertNotIn('database', result)
        # sanity check the connect args are still passed
        self.assertEqual(result,
            ['mysqladmin', '-u', 'u', '-poops', '-h', 'h'])

    def test_get_command_special_syntax_for_pg_restore(self):
        meta = type('mock', (object, ),
                {'username': '', 'hostname': '', 'port': '', 'password': 'oops',
                'path': '/database'})
        with mock.patch('postdoc.pg_connect_bits') as mock_bits:
            mock_bits.return_value = ['rofl']
            self.assertEqual(postdoc.get_command('pg_restore', meta),
                    ['pg_restore', 'rofl', '--dbname', 'database'])

    def test_get_command_special_syntax_for_mysql(self):
        meta = type('mock', (object, ),
            {'scheme': 'mysql', 'username': '', 'hostname': '', 'port': '',
            'password': 'oops', 'path': '/database'})
        with mock.patch('postdoc.connect_bits') as mock_bits:
            mock_bits.return_value = ['rofl']
            self.assertEqual(postdoc.get_command('mysql', meta),
                    ['mysql', 'rofl', '--database', 'database'])

    def test_main_exits_with_no_command(self):
        with mock.patch('postdoc.sys') as mock_sys:
            mock_sys.argv = ['phd']
            with self.assertRaises(SystemExit):
                postdoc.main()

    def test_main_exits_with_bad_command(self):
        with mock.patch('postdoc.sys') as mock_sys:
            mock_sys.argv = ['phd', 'fun']
            with self.assertRaises(SystemExit):
                postdoc.main()

    def test_main_exits_with_missing_env(self):
        mock_subprocess = mock.MagicMock()
        mock_get_command = mock.MagicMock(return_value=['get_command'])
        mock_sys = mock.MagicMock()
        mock_sys.argv = ['argv1', 'psql', 'argv3', 'argv4']

        with mock.patch.multiple(
            postdoc,
            subprocess=mock_subprocess,
            get_command=mock_get_command,
            sys=mock_sys,
        ):
            with self.assertRaises(SystemExit):
                postdoc.main()

    def test_main_can_use_alternate_url(self):
        mock_subprocess = mock.MagicMock()
        mock_sys = mock.MagicMock(
            argv=['argv1', 'FATTYBASE_URL', 'psql', 'extra_arg'],
        )
        mock_os = mock.MagicMock(environ={
            'FATTYBASE_URL': 'postgis://u@h/test',
        })

        with mock.patch.multiple(
            postdoc,
            subprocess=mock_subprocess,
            sys=mock_sys,
            os=mock_os,
        ):
            postdoc.main()
            self.assertEqual(mock_subprocess.call.call_args[0][0],
                ['psql', '-U', 'u', '-h', 'h', 'test', 'extra_arg'])

    def test_main_passes_password_in_env(self):
        my_password = 'hunter2'
        meta = type('mock', (object, ),
                {'password': my_password})
        self.assertNotIn('DATABASE_URL', os.environ,
            msg="Re-run tests in an environment without DATABASE_URL")
        mock_subprocess = mock.MagicMock()
        mock_get_command = mock.MagicMock(return_value=['get_command'])
        mock_get_uri = mock.MagicMock(return_value=meta)
        mock_sys = mock.MagicMock()
        mock_sys.argv = ['foo', 'psql']

        with mock.patch.multiple(
            postdoc,
            subprocess=mock_subprocess,
            get_command=mock_get_command,
            get_uri=mock_get_uri,
            sys=mock_sys,
        ):
            postdoc.main()
        self.assertEqual(
            mock_subprocess.call.call_args[1]['env']['PGPASSWORD'],
            my_password)

    def test_main_appends_additional_flags(self):
        self.assertNotIn('DATABASE_URL', os.environ,
            msg="Re-run tests in an environment without DATABASE_URL")
        mock_subprocess = mock.MagicMock()
        mock_get_command = mock.MagicMock(return_value=['get_command'])
        mock_get_uri = mock.MagicMock()
        mock_sys = mock.MagicMock()
        mock_sys.argv = ['argv1', 'psql', 'argv3', 'argv4']

        with mock.patch.multiple(
            postdoc,
            subprocess=mock_subprocess,
            get_command=mock_get_command,
            get_uri=mock_get_uri,
            sys=mock_sys,
        ):
            postdoc.main()
            self.assertEqual(
                mock_subprocess.call.call_args[0][0],
                ['get_command', 'argv3', 'argv4']
            )

    def test_nonsense_command_has_meaningful_error(self):
        mock_os = mock.MagicMock(environ={
            'DATABASE_URL': 'postgis://u@h/test',
        })
        mock_sys = mock.MagicMock(
            argv=['phd', 'xyzzy'])
        with mock.patch.multiple(
            postdoc,
            os=mock_os,
            sys=mock_sys,
        ):
            with self.assertRaises(SystemExit):
                postdoc.main()


if __name__ == '__main__':
    unittest.main()
