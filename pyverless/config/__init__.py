# -*- coding: utf-8 -*-
"""
pyverless.config
"""
import importlib
import os
from yaml import load

ENVIRONMENT_VARIABLE = "PYVERLESS_SETTINGS"
BASE_SETTINGS_MODULE = 'pyverless.config.base_settings'


class Settings:
    """
    Settings
    """

    def __init__(self, source=None):
        """
        Load the settings source pointed to by the environment variable.
        The source may be one of the following:
        - A Python module
        - A YAML file (.yml/.yaml)
        """

        # load user settings from module or yaml file. The source can be passed
        # on istantiation of Settings or through ENVIRONMENT_VARIABLE
        if not source:
            try:
                source = os.environ[ENVIRONMENT_VARIABLE]
            except KeyError:
                raise Exception(
                    "No settings defined. You must either define the environment variable %s "
                    "pointing to a python module or YAML file or instantiate Settings."
                    % ENVIRONMENT_VARIABLE)

        # load base settings from base settings module
        self.load_from_module(BASE_SETTINGS_MODULE)

        # Obtain extension
        _, filext = source.rsplit('.', 1)

        # load user settings from yaml file
        if filext in ['yml', 'yaml']:
            self.load_from_yaml_file(source)
        # load user settings from python module
        else:
            self.load_from_module(source)

    def load_from_yaml_file(self, file):
        """
        load_from_yaml_file
        """
        with open(file, mode='rb') as yaml_file:
            settings = load(yaml_file)

        if settings:  # setting file might be empty
            for setting, value in settings.items():
                setattr(self, setting, value)

    def load_from_module(self, module):
        """
        load_from_module
        """
        settings_module = importlib.import_module(module)

        # load user settings
        for setting in dir(settings_module):
            if setting.isupper():
                setattr(self, setting, getattr(settings_module, setting))


settings = Settings()
