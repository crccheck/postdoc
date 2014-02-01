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
    return urlparse(os.environ.get(env))


def connect_bits(meta):
    """Turn the url into connection bits."""
    bits = []
    if meta.username:
        bits.extend(['-U', meta.username])
    if meta.hostname:
        bits.extend(['-h', meta.hostname])
    if meta.port:
        bits.extend(['-p', str(meta.port)])
    return bits


def pg_command(command, meta):
    """Construct the command."""
    bits = []
    # password as environment varariable
    if meta.password:
        bits.append('PGPASSWORD=%s' % meta.password)
    # command to run
    bits.append(command)
    # connection params
    bits.extend(connect_bits(meta))
    # database name
    bits.append(meta.path[1:])
    # outtahere
    return bits


def main():
    if len(sys.argv) < 2:
        exit('Usage: phd COMMAND [additional-options]\n\n'
            '  ERROR: Must give a COMMAND like psql, createdb, dropdb'
        )
    if sys.argv[1] not in VALID_COMMANDS:
        exit('Usage: phd COMMAND [additional-options]\n\n'
            '  ERROR: "%s" is not a known postgres command' % sys.argv[1]
        )

    try:
        tokens = pg_command(sys.argv[1], get_uri())
    except AttributeError:
        exit('Usage: phd COMMAND [additional-options]\n\n'
            '  ERROR: DATABASE_URL is not set'
        )
    # pass any other flags the user set along
    tokens.extend(sys.argv[2:])
    subprocess.call(tokens)


if __name__ == '__main__':
    main()
