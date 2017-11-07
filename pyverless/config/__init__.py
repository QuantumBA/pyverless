# -*- coding: utf-8 -*-
"""
pyverless.config
"""
import os
import types
import errno

ENVIRONMENT_VARIABLE = "PYVERLESS_SETTINGS"
here = os.path.dirname(os.path.realpath(__file__))


class Settings(object):
    """Works exactly like a dict but provides ways to fill it from files
    or special dictionaries.  There are two common patterns to populate the
    config.
    Either you can fill the config from a config file::
        app.config.from_pyfile('yourconfig.cfg')
    Or alternatively you can define the configuration options in the
    module that calls :meth:`from_object` or provide an import path to
    a module that should be loaded.  It is also possible to tell it to
    use the same module and with that provide the configuration values
    just before the call::
        DEBUG = True
        SECRET_KEY = 'development key'
        app.config.from_object(__name__)
    In both cases (loading from any Python file or loading from modules),
    only uppercase keys are added to the config.  This makes it possible to use
    lowercase values in the config file for temporary values that are not added
    to the config or to define the config keys in the same file that implements
    the application.
    Probably the most interesting way to load configurations is from an
    environment variable pointing to a file::
        app.config.from_envvar('YOURAPPLICATION_SETTINGS')
    In this case before launching the application you have to set this
    environment variable to the file you want to use.  On Linux and OS X
    use the export statement::
        export YOURAPPLICATION_SETTINGS='/path/to/config/file'
    On windows use `set` instead.
    :param root_path: path to which files are read relative from.  When the
                      config object is created by the application, this is
                      the application's :attr:`~flask.Flask.root_path`.
    :param defaults: an optional dictionary of default values
    """

    def __init__(self):
        """
        Load the settings module pointed to by the environment variable.
        """
        settings_file = os.environ.get(ENVIRONMENT_VARIABLE)

        self._wrapped = self.load_settings(settings_file)

    def __getattr__(self, name):
        """Return the value of a setting and cache it in self.__dict__."""
        val = getattr(self._wrapped, name)
        self.__dict__[name] = val
        return val

    def load_settings(self, filename=None, silent=False):
        """Updates the values in the config from a Python file.  This function
        behaves as if the file was imported as module with the
        :meth:`from_object` function.
        :param filename: the filename of the config.  This can either be an
                         absolute filename or a filename relative to the
                         root path.
        :param silent: set to ``True`` if you want silent failure for missing
                       files.
        .. versionadded:: 0.7
           `silent` parameter.
        """

        # load base settings
        self.load_base_settings()

        # load user settings
        if filename:
            obj = types.ModuleType('config')
            obj.__file__ = filename
            try:
                with open(filename, mode='rb') as config_file:
                    exec(compile(config_file.read(), filename, 'exec'), obj.__dict__)
            except IOError as e:
                if silent and e.errno in (errno.ENOENT, errno.EISDIR):
                    return False
                e.strerror = 'Unable to load configuration file (%s)' % e.strerror
                raise

            for key in dir(obj):
                if key.isupper():
                    setattr(self, key, getattr(obj, key))

        return True

    def load_base_settings(self):
        base_settings_file = os.path.join(here, 'base_config.py')
        obj = types.ModuleType('config')
        obj.__file__ = base_settings_file

        with open(base_settings_file, mode='rb') as config_file:
            exec(compile(config_file.read(), base_settings_file, 'exec'), obj.__dict__)

        for key in dir(obj):
            if key.isupper():
                setattr(self, key, getattr(obj, key))


settings = Settings()
