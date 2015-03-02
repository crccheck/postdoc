PostDoc
=======

A helper for Postgres + Docker that works for free

.. image:: https://travis-ci.org/crccheck/postdoc.png?branch=master
    :target: https://travis-ci.org/crccheck/postdoc

About
-----

A wrapper that wraps a postgres command with connection arguments according to
the DATABASE_URL environment variable.

I originally made this because manually typing the connection args to ``pqsl``,
``createdb``, etc. became tiring. "Ain't nobody got time for dat".

Let's say your environment is like this::

    $ env | grep DATABASE_URL
    DATABASE_URL=postgres://docker@127.0.0.1/elevators

You *could* type::

    $ createdb -U docker -h 127.0.0.1 elevators
    createdb elevators

Or with ``PostDoc``::

    $ phd createdb
    createdb -U docker -h 127.0.0.1 elevators
    createdb elevators

Docker doesn't really have anything to do with this. But now that I've been
using Docker to manage my Postgres databases, I can't use defaults anymore.

But wait, there's more!

You can do MySQL stuff too::

    $ phd mysql
    mysql -u docker -h 127.0.0.1 --database elevators
    Reading table information for completion of table and column names
    You can turn off this feature to get a quicker startup with -A

    $ phd mysqlcheck --auto-repair
    mysqlcheck -u docker -h 127.0.0.1 elevators --auto-repair

If your database url isn't `DATABASE_URL`, you can connect to it by making it
the first argument::

    $ export FATTYBASE_URL=postgres://fatty@fat/phat
    $ phd FATTYBASE_URL psql
    psql -U fatty -h fat phat


Installation
------------

Install with pip::

    pip install postdoc


Extras
------

Add the flag `--postdoc-dry-run` to just print the command.

Add the flag `--postdoc-quiet` to execute the command without printing the
debugging line.

Aliases::

    alias dphd="phd --postdoc-dry-run"
    alias qphd="phd --postdoc-quiet"




.. image:: http://i.imgur.com/qqperK4.jpg
