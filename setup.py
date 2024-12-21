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
        os.system("rm -vrf ./WeatherWatch.log*")
        os.system("rm -vrf ./report.html")
        os.system("rm -vrf ./reports")
        os.system("rm -vrf ./*.egg-info")
        os.system("rm -vrf ./.coverage")
        os.system("rm -vrf ./coverage")
        os.system("rm -vrf ./pix")
        os.system("rm -vrf ./vid")
        os.system("rm -vrf ./backup")
        os.system("find . -name \"__pycache__\" -type d -exec sudo rm -vfR {} \;")

# run black isort flake8
class FormatCommand(Command):
    """Custom format command to run formating and style checks."""

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.system("poetry run black weatherwatch")
        os.system("poetry run isort weatherwatch")
        os.system("poetry run flake8 weatherwatch")

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
        os.system("coverage run -m pytest")
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
        
        sonar_url = os.environ.get('SONAR_URL') 
        #print(sonar_url)

        sonar_token = os.environ.get('WEATHER_SONAR_TOKEN') 
        #print(sonar_token)
        
        os.system("sonar-scanner -X " + 
                  "-Dsonar.projectKey=WeatherWatch " + 
                  "-Dsonar.python.version=3 " +
                  "-Dsonar.sources=weatherwatch " +
                  "-Dsonar.exclusions=src/lib/**/* " +
                  f"-Dsonar.host.url={sonar_url} " + 
                  f"-Dsonar.login={sonar_token}")

# load sample data
class SQLInitCommand(Command):
    """loads 8 days of sample data into tables"""

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.system("python3 weatherwatch/SampleLoader.py")

class DockerMysqlUpCommand(Command):
    """launch mysql docker container"""

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.system("docker compose --file mariadb-docker-compose.yml up -d")

class DockerMysqlDownCommand(Command):
    """shutdown mysql docker container"""

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.system("docker compose --file mariadb-docker-compose.yml down")

# load sample data
class ReportCPCommand(Command):
    """copy test results to net share"""

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        
        os.system("sudo rm -fR /mnt/clones/data/test/*")
        os.system("sudo cp -r reports/* /mnt/clones/data/test/")

# test run via poetry
# this is to hold cm util scripts
setup(
    packages=find_packages(),
    cmdclass={"clean": CleanCommand, 
              "format": FormatCommand, 
              "cover": CoverageCommand, 
              "reportcp": ReportCPCommand, 
              "sonar": SonarCommand,
              "dbInit": SQLInitCommand,
              'mysqlUp': DockerMysqlUpCommand,
              'mysqlDown': DockerMysqlDownCommand},
)
