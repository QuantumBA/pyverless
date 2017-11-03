import os
import sys

here = os.path.dirname(os.path.realpath(__file__))

pyverless_settings = os.path.join(here, 'test_config/config.py')

os.environ['PYVERLESS_SETTINGS'] = pyverless_settings

sys.path.append(here)
