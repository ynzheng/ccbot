#!/bin/bash
set -e

name=botvsext
pyminifier -o $name.pyx $name.py
python3 cysetup_$name.py build_ext --inplace
strip -g $name.cpython-3*-x86_64-linux-gnu.so
