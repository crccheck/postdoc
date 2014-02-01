# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import unittest

import mock

import postdoc


class PHDTest(unittest.TestCase):
    def test_get_uri(self):
        with mock.patch('postdoc.os') as mock_os:
            mock_os.environ = {
                'DATABASE_URL': 'foo',
                'FATTYBASE_URL': 'bar',
            }
            self.assertEqual(postdoc.get_uri().path, 'foo')
            self.assertEqual(postdoc.get_uri('FATTYBASE_URL').path, 'bar')

    def test_connect_bits_trivial_case(self):
        meta = type('mock', (object, ),
                {'username': '', 'hostname': '', 'port': ''})
        result = postdoc.connect_bits(meta)
        self.assertEqual(result, [])

    def test_connect_bits_has_everything(self):
        meta = type('mock', (object, ),
                {'username': '1', 'hostname': '2', 'port': 3})
        result = postdoc.connect_bits(meta)
        self.assertEqual(result, ['-U', '1', '-h', '2', '-p', '3'])

    def test_pg_command_assembles_bits_in_right_order(self):
        meta = type('mock', (object, ),
                {'username': '', 'hostname': '', 'port': '', 'password': '',
                'path': '/database'})
        with mock.patch('postdoc.connect_bits') as mock_bits:
            mock_bits.return_value = ['lol']
            self.assertEqual(postdoc.pg_command('foo', meta),
                    ['foo', 'lol', 'database'])

    def test_pg_command_prepends_password(self):
        meta = type('mock', (object, ),
                {'username': '', 'hostname': '', 'port': '', 'password': 'oops',
                'path': '/database'})
        with mock.patch('postdoc.connect_bits') as mock_bits:
            mock_bits.return_value = ['rofl']
            self.assertEqual(postdoc.pg_command('bar', meta),
                    ['PGPASSWORD=oops', 'bar', 'rofl', 'database'])

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

    def test_main_appends_additional_flags(self):
        mock_subprocess = mock.MagicMock()
        mock_pg_command = mock.MagicMock(return_value=['pg_command'])
        mock_sys = mock.MagicMock()
        mock_sys.argv = ['argv1', 'psql', 'argv3', 'argv4']
        mock_get_uri = mock.MagicMock()

        with mock.patch.multiple(postdoc,
            subprocess=mock_subprocess,
            pg_command=mock_pg_command,
            get_uri=mock_get_uri,
            sys=mock_sys,
        ):
            postdoc.main()
            print mock_subprocess.call
            mock_subprocess.call.assert_called_once_with(
                    ['pg_command', 'argv3', 'argv4'])


if __name__ == '__main__':
    unittest.main()
