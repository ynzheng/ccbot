#!/bin/bash
set -e

pyminifier -o symarbit.pyx symarbit.py
python3 cysetup.py build_ext --inplace
strip -g symarbit.cpython-3*-x86_64-linux-gnu.so
