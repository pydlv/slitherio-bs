import sys
# its win32, maybe there is win64 too?
IS_WINDOWS = sys.platform.startswith('win')

OBSERVATION_SIZE = (80, 80)
LEARNING_RATE = 0.1