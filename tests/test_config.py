import os
from pyverless.config import Settings, settings

here = os.path.dirname(os.path.realpath(__file__))


class TestConfig():

    def test_settings_from_environment_variable(self):
        # Note: Variable PYVERLESS_SETTINGS is set in __init__.py
        # within this tests module

        # The following settings are found in test_config.settings
        assert settings.SECRET_KEY == 'test-secret-key'
        assert settings.USER_MODEL == 'test_config.models.User'

        # The following setting is found in pyverless.config.base_settings
        assert settings.JWT_ALGORITHM == 'HS256'

    def test_settings_from_module(self):
        settings = Settings('test_config.settings')

        # The following settings are found in test_config.settings
        assert settings.SECRET_KEY == 'test-secret-key'
        assert settings.USER_MODEL == 'test_config.models.User'

        # The following setting is found in pyverless.config.base_settings
        assert settings.JWT_ALGORITHM == 'HS256'

    def test_settings_from_yaml(self):
        path_to_yml = os.path.join(here, 'test_config/settings.yml')
        settings = Settings(path_to_yml)

        # The following settings are found in test_config/settings.yml
        assert settings.SECRET_KEY == 'test-secret-key-from-yml'
        assert settings.USER_MODEL == 'test_config.models.UserFromYAML'

        # The following setting is found in pyverless.config.base_settings
        assert settings.JWT_ALGORITHM == 'HS256'
