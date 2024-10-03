# https://stackoverflow.com/questions/1896918/running-unittest-with-typical-test-directory-structure
# this is needed to reference src modules
import os
import sys

PROJECT_PATH = os.getcwd()
SOURCE_PATH = os.path.join(PROJECT_PATH, "weatherwatch")
sys.path.append(SOURCE_PATH)
