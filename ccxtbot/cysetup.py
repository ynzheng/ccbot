from distutils.core import setup
from Cython.Build import cythonize

from distutils import sysconfig
import platform


if platform.system() != 'Windows':  # When compilinig con visual no -g is added to params
    cflags = sysconfig.get_config_var('CFLAGS')
    opt = sysconfig.get_config_var('OPT')
    sysconfig._config_vars['CFLAGS'] = cflags.replace(' -g ', ' ')
    sysconfig._config_vars['OPT'] = opt.replace(' -g ', ' ')

if platform.system() == 'Linux':  # In macos there seems not to be -g in LDSHARED
    ldshared = sysconfig.get_config_var('LDSHARED')
    sysconfig._config_vars['LDSHARED'] = ldshared.replace(' -g ', ' ')

setup(ext_modules = cythonize(
        "symarbit.pyx",
        #gdb_debug=False,
        #language="c++",
     ))
