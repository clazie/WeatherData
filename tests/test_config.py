# import pytest
from src.confighelper import ConfigHelper
from os import environ
from dotenv import load_dotenv


def test_dummy():
    assert 1 == 1


def test_initialized_false():
    config = ConfigHelper()
    assert config.filename is None
    assert not config._initialized


def test_filename_from_environment():
    environ["CONFIG"] = "./tests/config-tests.yaml"
    config = ConfigHelper()
    config.initialize()
    assert config._initialized
    environ.clear()


def test_filename_from_dotenv_file():
    # Environment CONFIG must not be set
    assert environ.get("CONFIG", None) is None
    load_dotenv("./tests/.env-test")
    config = ConfigHelper()
    config.initialize(None, "./tests/.env-test")
    # Environment should be set from .env file
    assert environ.get("CONFIG", None) == "./tests/config-tests.yaml"
    assert config._initialized
    environ.clear()


def test_initialized_true():
    environ.clear()
    config = ConfigHelper()
    config.initialize("./tests/config-tests.yaml")
    assert config._initialized


def test_configuration():
    environ.clear()
    decivename = "NODENAME"
    gateway = "GATEWAY"
    broker = "BROKER"
    port = 1234
    user = "USERNAME"
    password = "PASSWORD"
    clientid = "CLIENTID"
    prefix = "PREFIX"
    version = "PROTOKOLLVERSION"
    config = ConfigHelper()
    config.initialize("./tests/config-tests.yaml")
    assert config.get_var('base.devicename') == decivename
    assert config.get_var('base.gateway') == gateway
    assert config.get_var('broker.ip') == broker
    assert config.get_var('broker.port') == port
    assert config.get_var('broker.user') == user
    assert config.get_var('broker.password') == password
    assert config.get_var('broker.clientid') == clientid
    assert config.get_var('broker.prefix') == prefix
    assert config.get_var('broker.version') == version


def test_check_config_default():
    config = ConfigHelper()
    config.initialize("./config-default.yaml")
    assert config.get_var('influxdb.password') == 'adminpassword'
    assert config.get_var('mqtt.port') == 1883
    assert config.get_var('mqtt.user') == 'username'
    assert config.get_var('mqtt.password') == 'password'
    assert config.get_var('ecowitt.appkey') == 'FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF'
    assert config.get_var('ecowitt.apikey') == '5f3f78bf-25f7-4f03-9df4-6f7688268ef4'
    assert config.get_var('weatherunderground.apikey') == '72f2fdfb972f4457f2fdfb972f1457cf'
    assert config.get_var('weatherunderground.stationid') == 'IBIEBF55'

# TODO: Check Yaml Crash
