#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__license__ = 'GPL v3'
__copyright__ = '2015, Kovid Goyal <kovid at kovidgoyal.net>'

import sys
import codecs

_plat = sys.platform.lower()
iswindows = 'win32' in _plat or 'win64' in _plat
ismacos = isosx = 'darwin' in _plat
isnewosx = ismacos and getattr(sys, 'new_app_bundle', False)
isfreebsd = 'freebsd' in _plat
isnetbsd = 'netbsd' in _plat
isdragonflybsd = 'dragonfly' in _plat
isbsd = isfreebsd or isnetbsd or isdragonflybsd
ishaiku = 'haiku1' in _plat
islinux = not (iswindows or ismacos or isbsd or ishaiku)
isfrozen = hasattr(sys, 'frozen')
isunix = ismacos or islinux or ishaiku
ispy3 = sys.version_info.major > 2
isxp = isoldvista = False

filesystem_encoding = sys.getfilesystemencoding()
if filesystem_encoding is None:
    filesystem_encoding = 'utf-8'
else:
    try:
        if codecs.lookup(filesystem_encoding).name == 'ascii':
            filesystem_encoding = 'utf-8'
            # On linux, unicode arguments to os file functions are coerced to an ascii
            # bytestring if sys.getfilesystemencoding() == 'ascii', which is
            # just plain dumb. This is fixed by the icu.py module which, when
            # imported changes ascii to utf-8
    except Exception:
        filesystem_encoding = 'utf-8'
