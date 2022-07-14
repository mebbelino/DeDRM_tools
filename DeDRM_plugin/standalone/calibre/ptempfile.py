__license__   = 'GPL v3'
__copyright__ = '2008, Kovid Goyal <kovid at kovidgoyal.net>'
"""
Provides platform independent temporary files that persist even after
being closed.
"""
import tempfile, os, atexit

from standalone.calibre.constants import (filesystem_encoding, iswindows, ismacos)


def cleanup(path):
    try:
        import os as oss
        if oss.path.exists(path):
            oss.remove(path)
    except:
        pass


_base_dir = None


def remove_dir(x):
    try:
        import shutil
        shutil.rmtree(x, ignore_errors=True)
    except:
        pass


def determined_remove_dir(x):
    for i in range(10):
        try:
            import shutil
            shutil.rmtree(x)
            return
        except:
            import os  # noqa
            if os.path.exists(x):
                # In case some other program has one of the temp files open.
                import time
                time.sleep(0.1)
            else:
                return
    try:
        import shutil
        shutil.rmtree(x, ignore_errors=True)
    except:
        pass


def app_prefix(prefix):
    if iswindows:
        return '%s_'%__appname__
    return '%s_%s_%s'%(__appname__, __version__, prefix)


_osx_cache_dir = None


def osx_cache_dir():
    global _osx_cache_dir
    if _osx_cache_dir:
        return _osx_cache_dir
    if _osx_cache_dir is None:
        _osx_cache_dir = False
        import ctypes
        libc = ctypes.CDLL(None)
        buf = ctypes.create_string_buffer(512)
        l = libc.confstr(65538, ctypes.byref(buf), len(buf))  # _CS_DARWIN_USER_CACHE_DIR = 65538
        if 0 < l < len(buf):
            try:
                q = buf.value.decode('utf-8').rstrip('\0')
            except ValueError:
                pass
            if q and os.path.isdir(q) and os.access(q, os.R_OK | os.W_OK | os.X_OK):
                _osx_cache_dir = q
                return q


def force_unicode(x):
    # Cannot use the implementation in calibre.__init__ as it causes a circular
    # dependency
    if isinstance(x, bytes):
        x = x.decode(filesystem_encoding)
    return x


def _make_file(suffix, prefix):
    suffix, prefix = map(force_unicode, (suffix, prefix))  # no2to3
    return tempfile.mkstemp(suffix, prefix)


def _make_dir(suffix, prefix, base):
    suffix, prefix = map(force_unicode, (suffix, prefix))  # no2to3
    return tempfile.mkdtemp(suffix, prefix, base)


class PersistentTemporaryFile:

    """
    A file-like object that is a temporary file that is available even after being closed on
    all platforms. It is automatically deleted on normal program termination.
    """
    _file = None

    def __init__(self, suffix="", prefix="", dir=None, mode='w+b'):
        if prefix is None:
            prefix = ""
        if dir is None:
            dir = "" # TODO implement base_dir() functionality
        fd, name = _make_file(suffix, prefix)

        self._file = os.fdopen(fd, mode)
        self._name = name
        self._fd = fd
        atexit.register(cleanup, name)

    def __getattr__(self, name):
        if name == 'name':
            return self.__dict__['_name']
        return getattr(self.__dict__['_file'], name)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def __del__(self):
        try:
            self.close()
        except:
            pass
