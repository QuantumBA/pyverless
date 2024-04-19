import os
import sys

here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(here)

os.environ['PYVERLESS_SETTINGS'] = 'config_test.settings'
