# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import os
import subprocess
import sys
try:
    # Python 3
    from urllib.parse import urlparse
except ImportError:
    # Python 2
    from urlparse import urlparse


__name__ = 'postdoc'
__version__ = '0.2.0'

# DEPRECATED, too many commands to whitelist now
# http://www.postgresql.org/docs/9.3/static/reference-client.html
VALID_COMMANDS = (
    'clusterdb',
    'createdb',
    'createlang',
    'createuser',
    'dropdb',
    'droplang',
    'dropuser',
    'ecpg',
    'pg_basebackup',
    'pg_config',
    'pg_dump',
    'pg_dumpall',
    'pg_isready',
    'pg_receivexlog',
    'pg_restore',
    'psql',
    'reindexdb',
    'vacuumdb',
)


def get_uri(env='DATABASE_URL'):
    """Grab and parse the url from the environment."""
    # trick python3's urlparse into raising an exception
    return urlparse(os.environ.get(env, 1337))


def pg_connect_bits(meta):
    """Turn the url into connection bits."""
    bits = []
    if meta.username:
        bits.extend(['-U', meta.username])
    if meta.hostname:
        bits.extend(['-h', meta.hostname])
    if meta.port:
        bits.extend(['-p', str(meta.port)])
    return bits


def mysql_connect_bits(meta):
    """Turn the url into connection bits."""
    bits = []
    if meta.username:
        bits.extend(['-u', meta.username])
    if meta.password:
        # password is one token
        bits.append('-p{0}'.format(meta.password))
    if meta.hostname:
        bits.extend(['-h', meta.hostname])
    if meta.port:
        bits.extend(['-P', str(meta.port)])
    return bits


def connect_bits(meta):
    bit_makers = {
        'mysql': mysql_connect_bits,
        'postgres': pg_connect_bits,
        'postgresql': pg_connect_bits,
        'postgis': pg_connect_bits,
    }
    scheme = getattr(meta, 'scheme', 'postgres')  # default to postgres
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
    if command == 'pg_restore':
        bits.append('--dbname')
    if command == 'mysql':
        bits.append('--database')
    bits.append(meta.path[1:])
    # outtahere
    return bits


def main():
    if '--version' in sys.argv:
        exit('PostDoc {0}'.format(__version__))
    if '--help' in sys.argv or len(sys.argv) < 2:
        exit('Usage: phd COMMAND [additional-options]\n\n'
            '  ERROR: Must give a COMMAND like psql, createdb, dropdb')
    # if sys.argv[1] not in VALID_COMMANDS:
    #     exit('Usage: phd COMMAND [additional-options]\n\n'
    #         '  ERROR: "%s" is not a known postgres command' % sys.argv[1])

    if sys.argv[1].isupper():
        environ_key = sys.argv[1]
        args = sys.argv[2:]
    else:
        environ_key = 'DATABASE_URL'
        args = sys.argv[1:]

    try:
        meta = get_uri(environ_key)
        # if we need to switch logic based off scheme multiple places, may want
        # to normalize it at this point
        tokens = get_command(args[0], meta)
    except AttributeError:
        exit('Usage: phd COMMAND [additional-options]\n\n'
            '  ERROR: DATABASE_URL is not set')
    env = os.environ.copy()
    # password as environment variable, set it for non-postgres schemas anyways
    if meta.password:
        env['PGPASSWORD'] = meta.password
    # pass any other flags the user set along
    tokens.extend(args[1:])
    sys.stderr.write(' '.join(tokens) + '\n')
    try:
        subprocess.call(tokens, env=env)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
