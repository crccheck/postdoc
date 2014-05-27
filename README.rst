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


Installation
------------

Install with pip::

    pip install postdoc







.. image:: http://i.imgur.com/qqperK4.jpg
