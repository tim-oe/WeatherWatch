#!/usr/bin/env python
# setup script
# https://docs.python.org/3/distutils/setupscript.html
# https://godatadriven.com/blog/a-practical-guide-to-using-setup-py/
# https://coderwall.com/p/3q_czg/custom-subcommand-at-setup-py
# TODO https://godatadriven.com/blog/a-practical-guide-to-setuptools-and-pyproject-toml/

import os
from setuptools import setup, find_packages, Command

# https://stackoverflow.com/questions/3779915/why-does-python-setup-py-sdist-create-unwanted-project-egg-info-in-project-r
# to clean cruft : py3clean .
# p3 setup.py clean
class CleanCommand(Command):
    """Custom clean command to tidy up the project root."""

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.system("py3clean -v .")
        os.system("rm -vrf ./report")
        os.system("rm -vrf ./*.egg-info")
        os.system("rm -vrf ./.coverage")

class CoverageCommand(Command):
    """
    coverage command
    https://coverage.readthedocs.io/en/6.3.2/#
    https://github.com/IBM/IBMDeveloper-recipes/blob/main/testing-and-code-coverage-with-python/index.md
    https://stackoverflow.com/questions/66914359/exclude-imports-from-coverage-in-python
    """

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.system("coverage run setup.py test")
        os.system("coverage html")
        os.system("coverage report")

# runs sonar static analizer
# https://docs.sonarcloud.io/advanced-setup/ci-based-analysis/sonarscanner-cli/
# p3 setup.py sonar
class SonarCommand(Command):
    """SonarQube scanner command"""

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.system("sonar-scanner -X " + 
                  "-Dsonar.projectKey=beez " + 
                  "-Dsonar.python.version=3 " +
                  "-Dsonar.sources=src " +
                  "-Dsonar.exclusions=src/lib/**/* " +
                  "-Dsonar.host.url=http://sonarqube " + 
                  "-Dsonar.login=sqp_71c96d128c55d2c7ecb534b89a9cfa35fe67a130")

# https://www.tutorialguruji.com/python/python-package-structure-setup-py-for-running-unit-tests/
# run tests
# via this script
# for single test class
# p3 setup tests -s <fully qualified test module>
setup(
    version="0.1",
    description="weather watch sensor processor",
    author="tim Cronin",
    author_email="tecronin@gmail.com",
    packages=find_packages(),
    install_requires=[],
    test_suite="tests",
    cmdclass={"clean": CleanCommand, "cover": CoverageCommand, "sonar": SonarCommand},
)
