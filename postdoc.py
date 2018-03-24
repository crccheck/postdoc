#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Usage: phd COMMAND [options] [command options]

  COMMAND  A command like psql, createdb, dropdb

Options:

  --postdoc-dry-run  Print output and then exit.
  --postdoc-quiet    Don't print debugging output.
"""

from __future__ import unicode_literals
import os
import subprocess
import sys
try:
    # Python 3
    from urllib.parse import urlparse
    from urllib.parse import unquote
except ImportError:
    # Python 2
    from urlparse import urlparse
    from urllib import unquote


__version__ = '1.0.0'


def get_uri(env_var='DATABASE_URL'):
    """Grab and parse the url from the environment."""
    parsed_result = urlparse(
        # Trick python3's urlparse into raising when env var is missing
        os.environ.get(env_var, 1337)
    )
    meta = {
        'scheme': parsed_result.scheme,
        'username': unquote(parsed_result.username or ''),
        'password': unquote(parsed_result.password or ''),
        'hostname': parsed_result.hostname,
        'port': parsed_result.port,
        'path': unquote(parsed_result.path or '/'),
    }
    return meta


def pg_connect_bits(meta):
    """Turn the url into connection bits."""
    bits = []
    if meta['username']:
        bits.extend(['-U', meta['username']])
    if meta['hostname']:
        bits.extend(['-h', meta['hostname']])
    if meta['port']:
        bits.extend(['-p', str(meta['port'])])
    return bits


def mysql_connect_bits(meta):
    """Turn the url into connection bits."""
    bits = []
    if meta['username']:
        bits.extend(['-u', meta['username']])
    if meta['password']:
        # `password` is one token for mysql (no whitespace)
        bits.append('-p{0}'.format(meta['password']))
    if meta['hostname']:
        bits.extend(['-h', meta['hostname']])
    if meta['port']:
        bits.extend(['-P', str(meta['port'])])
    return bits


def connect_bits(meta):
    bit_makers = {
        'mysql': mysql_connect_bits,
        'postgres': pg_connect_bits,
        'postgresql': pg_connect_bits,
        'postgis': pg_connect_bits,
    }
    scheme = meta.get('scheme', 'postgres')  # Default to postgres
    # TODO raise a better error than KeyError with an unsupported scheme
    return bit_makers[scheme](meta)


def get_command(command, meta):
    """Construct the command."""
    bits = []
    # command to run
    bits.append(command)
    # connection params
    bits.extend(connect_bits(meta))
    # database name
    if command == 'mysqladmin':
        # these commands shouldn't take a database name
        return bits
    if command == 'pg_restore':
        bits.append('--dbname')
    if command == 'mysql':
        bits.append('--database')
    bits.append(meta['path'][1:])
    return bits


def make_tokens_and_env(sys_argv):
    """Get the tokens or quit with help."""
    if sys_argv[1].isupper():
        env_var = sys_argv[1]
        args = sys_argv[2:]
    else:
        env_var = 'DATABASE_URL'
        args = sys_argv[1:]

    try:
        meta = get_uri(env_var)
        # if we need to switch logic based off scheme multiple places, may want
        # to normalize it at this point
        tokens = get_command(args[0], meta)
    except AttributeError:
        exit('Usage: phd COMMAND [additional-options]\n\n'
             '  ERROR: "{0}" is not set in the environment'.format(env_var))
    env = os.environ.copy()
    # password as environment variable, set it for non-postgres schemas anyways
    if meta['password']:
        env['PGPASSWORD'] = meta['password']
    # pass any other flags the user set along
    tokens.extend(args[1:])
    return tokens, env


def main():
    if '--version' in sys.argv:
        exit('PostDoc {0}'.format(__version__))
    if '--help' in sys.argv or len(sys.argv) < 2:
        exit(__doc__)
    is_dry_run = '--postdoc-dry-run' in sys.argv
    if is_dry_run:
        sys.argv.remove('--postdoc-dry-run')
    is_quiet = '--postdoc-quiet' in sys.argv
    if is_quiet:
        sys.argv.remove('--postdoc-quiet')

    tokens, env = make_tokens_and_env(sys.argv)
    if is_dry_run:
        sys.stdout.write(' '.join(tokens) + '\n')
        exit(0)
    if not is_quiet:
        sys.stderr.write(' '.join(tokens) + '\n')
    try:
        subprocess.call(tokens, env=env)
    except OSError as e:
        import errno
        if e.errno == errno.ENOENT:  # No such file or directory
            exit('{0}: command not found'.format(tokens[0]))
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
