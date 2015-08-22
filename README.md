# mesos-xargs

[![Build Status](https://travis-ci.org/solarkennedy/mesos-xargs.svg)](https://travis-ci.org/solarkennedy/mesos-xargs)

Have a Mesos cluster and you just want to run stuff on it?

Ever wish you could just use `xargs`? No? Good. You are a sane person
and should use Hadoop like a **normal** person.

## Installation

Mesos python bindings are kinda a mess. The main mesos bindings need to be
installed with the main Mesos package. `mesos.cli` can be installed via `pip`.

This is mostly left up as an exercise to the reader...

## Running

    seq 1 10 | ./mesos_xargs.py echo

## Acknowledgements

I'm mostly a python noob here. There are a lot of giants' shoulders
I am standing upon here.

* James Porter's [hello world](http://jamesporter.me/2014/11/15/hello-mesos.html) framework
* Stock [example framework](https://github.com/apache/mesos/blob/master/src/examples/python/test_framework.py) from Mesos
