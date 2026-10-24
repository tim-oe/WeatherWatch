# setup script
# https://docs.python.org/3/distutils/setupscript.html
# https://godatadriven.com/blog/a-practical-guide-to-using-setup-py/
# https://coderwall.com/p/3q_czg/custom-subcommand-at-setup-py
# TODO https://godatadriven.com/blog/a-practical-guide-to-setuptools-and-pyproject-toml/

from pathlib import Path
import os
import shutil
import tempfile
from setuptools import setup, find_packages, Command
import subprocess

# https://github.com/merbanan/rtl_433/blob/master/docs/BUILDING.md
# to build rtl_433 : 
# p3 setup.py rtl433
class Rtl433Command(Command):
    """Custom clean command to tidy up the project root."""

    user_options = []

    def initialize_options(self):
        """
        noop
        """

    def finalize_options(self):
        """
        noop
        """

    def run(self):
        """
        run
        """

        rtl_433_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../rtl_433'))

        # Clean up old build directories
        build_dir = os.path.join(rtl_433_dir, 'build')
        clean_dir = os.path.join(rtl_433_dir, 'clean')
        
        if os.path.exists(build_dir):
            shutil.rmtree(build_dir)
        if os.path.exists(clean_dir):
            shutil.rmtree(clean_dir)

        commands = [
            ["cmake", "-B", "clean"],
            ["cmake", "-DFORCE_COLORED_BUILD:BOOL=ON", "-GNinja", "-B", "build"],
            ["cmake", "--build", "build", "-j", "4"],
            ["sudo", "cmake", "--build", "build", "--target", "install"]
        ]
        
        for cmd in commands:
            subprocess.run(cmd, cwd=rtl_433_dir, check=True)

# https://stackoverflow.com/questions/3779915/why-does-python-setup-py-sdist-create-unwanted-project-egg-info-in-project-r
# to clean cruft : py3clean .
# p3 setup.py clean
class CleanCommand(Command):
    """Custom clean command to tidy up the project root."""

    user_options = []

    def initialize_options(self):
        """
        noop
        """


    def finalize_options(self):
        """
        noop
        """


    def run(self):
        """
        run
        """

        commands = [
            ["py3clean","-v","."],
            ["rm","-vrf","./WeatherWatch.log*"],
            ["rm","-vrf","./report.html"],
            ["rm","-vrf","./reports"],
            ["rm","-vrf","./*.egg-info"],
            ["rm","-vrf","./.coverage"],
            ["rm","-vrf","./coverage"],
            ["rm","-vrf","./pix"],
            ["rm","-vrf","./vid"],
            ["rm","-vrf","./backup"]
        ]
        
        for cmd in commands:
            subprocess.run(cmd, check=True)

        subprocess.run(["rm -vrf ./WeatherWatch.log*"], 
            shell=True,
            check=True)
        
        # Handle the find command separately with shell=True
        subprocess.run(['find . -name "__pycache__" -type d -exec sudo rm -vfR {} \\;'], 
            shell=True, 
            check=True)

# run black isort flake8
class FormatCommand(Command):
    """Custom format command to run formating and style checks."""

    user_options = []

    def initialize_options(self):
        """
        noop
        """


    def finalize_options(self):
        """
        noop
        """


    def run(self):
        """
        run
        """
        os.system("poetry run black weatherwatch")
        os.system("poetry run isort weatherwatch")
        os.system("poetry run flake8 weatherwatch")

class LintCommand(Command):
    """pylint processing"""

    user_options = []

    def initialize_options(self):
        """
        noop
        """


    def finalize_options(self):
        """
        noop
        """


    def run(self):
        """
        run
        """
        report_dir: Path = Path("reports")
        report_dir.mkdir(parents=True, exist_ok=True)

        os.system("pylint weatherwatch | pylint-json2html -o reports/pylint.html")

class CoverageCommand(Command):
    """
    coverage command
    https://coverage.readthedocs.io/en/6.3.2/#
    https://github.com/IBM/IBMDeveloper-recipes/blob/main/testing-and-code-coverage-with-python/index.md
    https://stackoverflow.com/questions/66914359/exclude-imports-from-coverage-in-python
    """

    user_options = []

    def initialize_options(self):
        """
        noop
        """


    def finalize_options(self):
        """
        noop
        """


    def run(self):
        """
        run
        """
        os.system("coverage run -m pytest")
        os.system("coverage xml")
        os.system("coverage html")
        os.system("coverage report")

# runs sonar static analizer
# https://docs.sonarcloud.io/advanced-setup/ci-based-analysis/sonarscanner-cli/
# p3 setup.py sonar
class SonarCommand(Command):
    """SonarQube scanner command"""

    user_options = []

    def initialize_options(self):
        """
        noop
        """


    def finalize_options(self):
        """
        noop
        """


    def run(self):
        """
        run
        """
        
        sonar_url = os.environ.get('SONAR_URL') 
        #print(sonar_url)

        sonar_token = os.environ.get('WEATHER_SONAR_TOKEN') 
        #print(sonar_token)

        # pylint format for sonar
        print("runnning pylint")
        os.system("pylint weatherwatch --output-format=parseable > reports/pylint-report.txt")
        print("pylint complete")
        os.system(f"sonar-scanner -X -Dsonar.host.url={sonar_url} -Dsonar.login={sonar_token}")

def _read_pyway_conf(path=".pyway.conf"):
    """
    read the flat pyway config used by pyway migrate
    :param path: config path
    :return: the config keys
    """
    conf = {}
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith("#") or ":" not in line:
                continue
            key, value = line.split(":", 1)
            conf[key.strip()] = value.strip()
    return conf


def _cnf_quote(value):
    """
    quote a value for a mysql client defaults file
    :param value: the raw value
    :return: the quoted value
    """
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _mysql_bin():
    """
    client binary for the local server
    :return: mariadb or mysql
    """
    for name in ("mariadb", "mysql"):
        if shutil.which(name):
            return name
    raise SystemExit("mariadb or mysql client is required")


def _mysql(defaults_file, sql, database=None):
    """
    run a statement with credentials kept out of the process list
    :param defaults_file: mysql client defaults path
    :param sql: the statement
    :param database: optional default schema
    :return: stdout
    """
    command = [_mysql_bin(), f"--defaults-extra-file={defaults_file}", "--batch", "--skip-column-names"]
    if database:
        command.append(database)
    command.extend(["-e", sql])
    result = subprocess.run(command, check=False, text=True, capture_output=True)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "mysql command failed"
        raise SystemExit(detail)
    return result.stdout


class DBResetCommand(Command):
    """drop the local weather database and rerun pyway migrations"""

    user_options = []

    def initialize_options(self):
        """
        noop
        """

    def finalize_options(self):
        """
        noop
        """

    def run(self):
        """
        drop the database from .pyway.conf when it is local, then pyway migrate
        """
        conf = _read_pyway_conf()
        host = conf.get("database_host", "")
        if host not in ("127.0.0.1", "localhost"):
            raise SystemExit(f"dbReset only runs against a local database, .pyway.conf host is {host}")
        name = conf.get("database_name", "")
        if not name.replace("_", "").isalnum():
            raise SystemExit(f"refusing database name {name}")
        port = conf.get("database_port", "3306")
        user = os.environ.get("PYWAY_DATABASE_USERNAME")
        password = os.environ.get("PYWAY_DATABASE_PASSWORD")
        if not user or password is None:
            raise SystemExit("PYWAY_DATABASE_USERNAME and PYWAY_DATABASE_PASSWORD are required")

        defaults = None
        try:
            handle = tempfile.NamedTemporaryFile("w", delete=False)
            defaults = handle.name
            handle.write("[client]\nprotocol=tcp\n")
            handle.write(f"host={_cnf_quote(host)}\n")
            handle.write(f"port={port}\n")
            handle.write(f"user={_cnf_quote(user)}\n")
            handle.write(f"password={_cnf_quote(password)}\n")
            handle.close()
            os.chmod(defaults, 0o600)

            grants = _mysql(
                defaults,
                "SELECT PRIVILEGE_TYPE FROM information_schema.USER_PRIVILEGES "
                "WHERE GRANTEE = CONCAT(CHAR(39), SUBSTRING_INDEX(CURRENT_USER(), '@', 1), "
                "CHAR(39), '@', CHAR(39), SUBSTRING_INDEX(CURRENT_USER(), '@', -1), CHAR(39)) "
                "AND PRIVILEGE_TYPE IN ('CREATE', 'DROP', 'ALL PRIVILEGES')",
            )
            privileges = set(grants.split())
            can_recreate = {"CREATE", "DROP"}.issubset(privileges) or "ALL PRIVILEGES" in grants
            if can_recreate:
                print(f"dropping database {name} on {host}")
                _mysql(
                    defaults,
                    f"DROP DATABASE IF EXISTS `{name}`; "
                    f"CREATE DATABASE `{name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci",
                )
            else:
                print(f"dropping tables in {name} on {host}")
                drops = _mysql(
                    defaults,
                    "SET SESSION group_concat_max_len = 1000000; "
                    "SELECT IFNULL(GROUP_CONCAT(CONCAT('DROP TABLE IF EXISTS `', REPLACE(TABLE_NAME, '`', '``'), '`') "
                    "SEPARATOR '; '), 'SELECT 1') "
                    "FROM information_schema.TABLES "
                    f"WHERE TABLE_SCHEMA = '{name}' AND TABLE_TYPE = 'BASE TABLE'",
                    database=name,
                ).strip()
                _mysql(defaults, f"SET FOREIGN_KEY_CHECKS = 0; {drops}; SET FOREIGN_KEY_CHECKS = 1", database=name)
        finally:
            if defaults and os.path.exists(defaults):
                os.remove(defaults)

        pyway = ".venv/bin/pyway" if os.path.exists(".venv/bin/pyway") else "pyway"
        print("running pyway migrate")
        subprocess.run([pyway, "migrate"], check=True)


# load sample data
class SQLInitCommand(Command):
    """loads 8 days of sample data into tables"""

    user_options = []

    def initialize_options(self):
        """
        noop
        """


    def finalize_options(self):
        """
        noop
        """


    def run(self):
        """
        run
        """
        os.system("python3 weatherwatch/SampleLoader.py")

class DockerMysqlUpCommand(Command):
    """launch mysql docker container"""

    user_options = []

    def initialize_options(self):
        """
        noop
        """


    def finalize_options(self):
        """
        noop
        """


    def run(self):
        """
        run
        """
        os.system("docker compose --file mariadb-docker-compose.yml up -d")

class DockerMysqlDownCommand(Command):
    """shutdown mysql docker container"""

    user_options = []

    def initialize_options(self):
        """
        noop
        """


    def finalize_options(self):
        """
        noop
        """


    def run(self):
        """
        run
        """
        os.system("docker compose --file mariadb-docker-compose.yml down")

class ReportCPCommand(Command):
    """copy test results to net share"""

    user_options = []

    def initialize_options(self):
        """
        noop
        """


    def finalize_options(self):
        """
        noop
        """


    def run(self):
        """
        run
        """
        
        os.system("sudo rm -fR /mnt/clones/data/test/*")
        os.system("sudo cp -r reports/* /mnt/clones/data/test/")

# test run via poetry
# this is to hold cm util scripts
setup(
    packages=find_packages(),
    cmdclass={"clean": CleanCommand, 
              "cover": CoverageCommand, 
              "dbInit": SQLInitCommand,
              "dbReset": DBResetCommand,
              "format": FormatCommand, 
              "lint": LintCommand, 
              "reportcp": ReportCPCommand, 
              "rtl433": Rtl433Command, 
              'mysqlUp': DockerMysqlUpCommand,
              'mysqlDown': DockerMysqlDownCommand,
              "sonar": SonarCommand},
)
