# Pii Decide

[![version](https://img.shields.io/pypi/v/pii-decide)](https://pypi.org/project/pii-decide)
[![changelog](https://img.shields.io/badge/change-log-blue)](CHANGES.md)
[![license](https://img.shields.io/pypi/l/pii-decide)](LICENSE)
[![build status](https://github.com/piisa/pii-decide/actions/workflows/pii-decide-pr.yml/badge.svg)](https://github.com/piisa/pii-decide/actions)

This repository builds a Python package providing evaluation &amp; decision on
detected PII instances, by means of implemented "deciders", modules that
decide where a PII Instance is to be kept or it is to be ignored.

Right now it is a (mostly) dummy package, and it incorporates only one simple
decider that takes care of removing overlapping PII Instances by following a
simple rule (if two instances overlap, it just retains the longest one)


## Requirements

The package needs
 * at least Python 3.8
 * the [pii-data] base package


## Usage

The package can be used:
 * As an API, using the PiiDecider class
 * As a command-line tool


## Building

The provided [Makefile] can be used to process the package:
 * `make pkg` will build the Python package, creating a file that can be
   installed with `pip`
 * `make unit` will launch all unit tests (using [pytest], so pytest must be
   available)
 * `make install` will install the package in a Python virtualenv. The
   virtualenv will be chosen as, in this order:
     - the one defined in the `VENV` environment variable, if it is defined
     - if there is a virtualenv activated in the shell, it will be used
     - otherwise, a default is chosen as `/opt/venv/pii` (it will be
       created if it does not exist)


[pii-data]: https://github.com/piisa/pii-data
[Makefile]: Makefile
[usage document]: doc/usage.md

[pytest]: https://docs.pytest.org
