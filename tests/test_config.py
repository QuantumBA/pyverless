import os
from pyverless.config import Settings, settings

here = os.path.dirname(os.path.realpath(__file__))


class TestConfig():

    def test_settings_from_environment_variable(self):
        # Note: Variable PYVERLESS_SETTINGS is set in __init__.py
        # within this tests module

        # The following settings are found in config_test.settings
        assert settings.SECRET_KEY == 'test-secret-key'
        assert settings.USER_MODEL == 'config_test.models.User'

        # The following setting is found in pyverless.config.base_settings
        assert settings.JWT_ALGORITHM == 'HS256'

    def test_settings_from_module(self):
        settings = Settings('config_test.settings')

        # The following settings are found in config_test.settings
        assert settings.SECRET_KEY == 'test-secret-key'
        assert settings.USER_MODEL == 'config_test.models.User'

        # The following setting is found in pyverless.config.base_settings
        assert settings.JWT_ALGORITHM == 'HS256'

    def test_settings_from_yaml(self):
        path_to_yml = os.path.join(here, 'config_test/settings.yml')
        settings = Settings(path_to_yml)

        # The following settings are found in config_test/settings.yml
        assert settings.SECRET_KEY == 'test-secret-key-from-yml'
        assert settings.USER_MODEL == 'config_test.models.UserFromYAML'

        # The following setting is found in pyverless.config.base_settings
        assert settings.JWT_ALGORITHM == 'HS256'

    def test_settings_from_environ(self):
        del os.environ['PYVERLESS_SETTINGS']
        os.environ["SECRET_KEY"] = 'test-secret-key-from-env'
        os.environ["USER_MODEL"] = 'config_test.models.UserFromEnv'
        os.environ["JWT_ALGORITHM"] = 'HS256'
        settings = Settings()

        # The following settings are found in config_test/settings.yml
        assert settings.SECRET_KEY == 'test-secret-key-from-env'
        assert settings.USER_MODEL == 'config_test.models.UserFromEnv'

        # The following setting is found in pyverless.config.base_settings
        assert settings.JWT_ALGORITHM == 'HS256'
