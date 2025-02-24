#!/usr/bin/env python3
from influxdb import InfluxDBClient

# InfluxDB v2
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

import requests
import datetime
import pytz
import time
import paho.mqtt.client as mqtt
import jsons
import logging
import logging.handlers
import math

from confighelper import ConfigHelper
from dataclass import WeatherData


local = pytz.timezone("Europe/Berlin")

log = logging.getLogger(__name__)

config = ConfigHelper()
config.initialize()

# Do not start if no config exists
assert config._initialized

handler = logging.handlers.TimedRotatingFileHandler(
    config.get_var("logger.filename", "weather2influxdb.log"),
    when="midnight",
    backupCount=config.get_var("logger.backupcount", 3))
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)
log.setLevel(logging.DEBUG)

log.info("weather2influxdb started")

log.debug("Debug")
log.info("Info")
log.warning("Warning")
log.error("Error")

log.info(f"Configuration: {config.configuration}")


def Local_To_UTC(naive):
    try:
        pst_now = local.localize(naive, is_dst=None)
    except (pytz.NonExistentTimeError):
        pst_now = local.localize(naive, is_dst=True)
    except (pytz.AmbiguousTimeError):
        pst_now = local.localize(naive, is_dst=False)

    utc_now = pst_now.astimezone(pytz.utc)
    return utc_now


def F_to_C(f):
    return float((float(f) - 32) * 5.0 / 9.0)  # (von Fahrenheit in Celsius)


def C_to_F(c):
    return float(float(c) * 1.8 + 32)  # (von Celsius nach Fahrenheit)


def Inch_to_mm(inch: float) -> float:
  return float(inch * 25.4)


def Mph_to_Kmh(mph: float) -> float:
  return float(mph * 1.60934)


def InHg_to_hPa(inhg: float) -> float:
  return float(inhg / 0.029529983071445)


def PAbs_to_PRel(pressureabs: float, temperature: float, height: float) -> float:
  p0: float = 0.0
  try:
    # Berechnung des auf Meereshöhe reduzierten Luftdrucks
    # es wird die laut Wikipedia vom Deutschen Wetterdienst empfohlene
    # Barometrische Höhenformel verwendet
    g0 = 9.80665                                           # Normwert der Fallbeschleunigung
    R = 287.05                                             # Gaskonstante trockener Luft
    T = 273.15                                             # 0°C in Kelvin
    Ch = 0.12                                              # Beiwert zu E
    if (temperature < 9.1):
      E = 5.6402 * (-0.0916 + math.exp(0.06 * temperature))  # Dampfdruck des Wasserdampfanteils bei t < 9.1°C
    else:
      E = 18.2194 * (1.0463 - math.exp(-0.0666 * temperature))  # Dampfdruck des Wasserdampfanteils bei t >= 9.1°C
    a = 0.0065                                          # vertikaler Temperaturgradient
    xp = height * g0 / (R * (T + temperature + Ch * E + a * height / 2))  # Exponent für Formel
    p0 = pressureabs * math.exp(xp)                       # Formel für den NN-bezogenen Luftdruck laut Wikipedia
  except Exception as e:
   log.error(e)

  return p0


def get_ecowitt_weather():
  try:
    retvalue: WeatherData = WeatherData()

    # Doku der API unter https://doc.ecowitt.net/web/#/
    url = config.get_var("ecowitt.url", None)
    if url is None:
        raise "ecowitt url is not configured"
    appkey = config.get_var("ecowitt.appkey", None)
    if appkey is None:
        raise "ecowitt url is not configured"
    apikey = config.get_var("ecowitt.apikey", None)
    if apikey is None:
        raise "ecowitt url is not configured"
    mac = config.get_var("ecowitt.mac", None)
    if mac is None:
        raise "ecowitt url is not configured"

    # Url is someting like 'https://api.ecowitt.net/api/v3/device/real_time?application_key={}&api_key={}&mac={}&call_back=all'
    # Replace {} with configured values
    url = url.format(appkey, apikey, mac)
    log.info(f"EcoWitt Url: '{url}'")

    x = requests.get(url)
    log.debug(x.text)

    if (x.status_code == 200):
      log.info("Status code 200: data received")
      jsondata = x.json()
      log.debug(jsondata)
      if (jsondata["code"]) != 0:
        raise Exception(f"Code from returned weatherdata is {jsondata['code']}. Msg: {jsondata['msg']}")

      # Data Conversion
      retvalue.time = datetime.datetime.utcfromtimestamp(int(jsondata["time"])).strftime('%Y-%m-%d %H:%M:%S')
      jsonwdat = jsondata["data"]
      log.warning(jsons.dumps(jsonwdat))
      retvalue.outtemp = F_to_C(float(jsonwdat["outdoor"]["temperature"]["value"]))
      retvalue.outfeelslike = F_to_C(float(jsonwdat["outdoor"]["feels_like"]["value"]))
      retvalue.outapptemp = F_to_C(float(jsonwdat["outdoor"]["app_temp"]["value"]))
      retvalue.outdrewpoint = F_to_C(float(jsonwdat["outdoor"]["dew_point"]["value"]))
      retvalue.outhumidity = float(jsonwdat["outdoor"]["humidity"]["value"])
      retvalue.intemp = F_to_C(float(jsonwdat["indoor"]["temperature"]["value"]))
      retvalue.inhumidity = float(jsonwdat["indoor"]["humidity"]["value"])
      retvalue.solar = float(jsonwdat["solar_and_uvi"]["solar"]["value"])
      retvalue.uvi = float(jsonwdat["solar_and_uvi"]["uvi"]["value"])
      retvalue.rainrate = Inch_to_mm(float(jsonwdat["rainfall"]["rain_rate"]["value"]))
      retvalue.rainevent = Inch_to_mm(float(jsonwdat["rainfall"]["event"]["value"]))
      retvalue.rainhourly = Inch_to_mm(float(jsonwdat["rainfall"]["hourly"]["value"]))
      retvalue.raindaily = Inch_to_mm(float(jsonwdat["rainfall"]["daily"]["value"]))
      retvalue.rainweekly = Inch_to_mm(float(jsonwdat["rainfall"]["weekly"]["value"]))
      retvalue.rainmonthly = Inch_to_mm(float(jsonwdat["rainfall"]["monthly"]["value"]))
      retvalue.rainyearly = Inch_to_mm(float(jsonwdat["rainfall"]["yearly"]["value"]))
      retvalue.windspeed = Mph_to_Kmh(float(jsonwdat["wind"]["wind_speed"]["value"]))
      retvalue.windgust = Mph_to_Kmh(float(jsonwdat["wind"]["wind_gust"]["value"]))
      retvalue.winddirection = float(jsonwdat["wind"]["wind_direction"]["value"])
      retvalue.pressurerel = InHg_to_hPa(float(jsonwdat["pressure"]["relative"]["value"]))
      retvalue.pressureabs = InHg_to_hPa(float(jsonwdat["pressure"]["absolute"]["value"]))
      # retvalue.waterleak = float(jsonwdat["water_leak"]["leak_ch2"]["value"])  //API liefert wert nicht mehr
      retvalue.battery_t_rh_p_sensor = float(jsonwdat["battery"]["t_rh_p_sensor"]["value"])
      retvalue.battery_sensor_array = float(jsonwdat["battery"]["sensor_array"]["value"])

      return retvalue
    else:
        log.error(f"Status code {x.status_code}: No data received")
        return None
  except Exception as e:
      log.error(e)
      return None


def get_http_weather():
  try:
    retvalue: WeatherData = WeatherData()

    url = config.get_var("httpjson.url", None)
    if url is None:
        raise "httpjson url is not configured"

    height = config.get_var("base.stationheight", None)
    if height is None:
        raise "base height is not configured"

    x = requests.get(url)
    log.debug(x.text)
    # {"loc":"cz","dt":"2023-01-25 11:33:07","dw":"2023-01-25 11:33:07","to": "-1.11","ti": "3.39","ws": "2.9","wsa": "2.8085","wsg": "5.47","wd": "98","r": "100","r1h": "0","r24": "0","ho":  "99","hi": "73","p": "1009.48","ss": "0","cl": "0","ct": "0"}

    if (x.status_code == 200):
        log.info("received http json data")
        jsonwdat = x.json()
        retvalue.time = str(jsonwdat["dt"])
        retvalue.outtemp = float(jsonwdat["to"])
        retvalue.intemp = float(jsonwdat["ti"])
        retvalue.windspeed = float(jsonwdat["ws"])
        retvalue.windgust = float(jsonwdat["wsg"])
        retvalue.winddirection = float(jsonwdat["wd"])
        retvalue.rainyearly = float(jsonwdat["r"])
        retvalue.rainhourly = float(jsonwdat["r1h"])
        retvalue.raindaily = float(jsonwdat["r24"])
        retvalue.outhumidity = float(jsonwdat["ho"])
        retvalue.inhumidity = float(jsonwdat["hi"])
        retvalue.pressureabs = float(jsonwdat["p"])
        retvalue.pressurerel = PAbs_to_PRel(retvalue.pressureabs, retvalue.outtemp, height)

        return retvalue
    else:
        return None
  except Exception as e:
    log.error(e)
    return None


def get_weatherunderground_weather():
  try:
    retvalue: WeatherData = WeatherData()

    return retvalue
  except Exception as e:
    log.error(e)
    return None


def set_weather_influxdb(weatherdata: WeatherData):
  try:
    ifxhost = config.get_var("influxdb.host", None)
    if ifxhost is None:
      raise "influxdb host is not configured"
    ifxport = config.get_var("influxdb.port", None)
    if ifxport is None:
      raise "influxdb port is not configured"
    ifxuser = config.get_var("influxdb.user", None)
    if ifxuser is None:
      raise "influxdb user is not configured"
    ifxpassword = config.get_var("influxdb.password", None)
    if ifxpassword is None:
      raise "influxdb password is not configured"
    ifxdb = config.get_var("influxdb.database", None)
    if ifxdb is None:
      raise "influxdb ifxdb is not configured"

    client = InfluxDBClient(host=ifxhost, port=ifxport, username=ifxuser, password=ifxpassword)
    client.switch_database(ifxdb)

    # weatherdata = parsed_json_all['data']

    datapoint = [{
        "measurement": "Weather",
        "time": weatherdata.time,
        "fields": {
            "OutTemp": weatherdata.outtemp,
            "InTemp": weatherdata.intemp,
            "OutHumitity": weatherdata.outhumidity,
            "InHumidity": weatherdata.inhumidity,
            "Rain": weatherdata.rainrate,
            "Rain1h": weatherdata.rainhourly,
            "Rain24h": weatherdata.raindaily,
            "Pressure": weatherdata.pressureabs,
            "Wind": weatherdata.windspeed,
            # "WindAvg": float(weatherdata["wind"]["wind_speed"]["value"]) *1.60934,
            "WindGust": weatherdata.windgust,
            # "CL": 0,
            # "CT": 0,
            # "Status": parsed_json["qcStatus"],
            # "PNow": float(solar["Gesamtleistung_AC"]),
            "WindDir": weatherdata.winddirection
        }
    }]

    log.debug(f"Return client.write_points(datapoint) is {client.write_points(datapoint)}")
    log.debug(f"Datapoint is: {datapoint}")
    log.info("Inserted dataset")
  except Exception as e:
    log.error(e)


def set_weather_influxdb2(weatherdata: WeatherData):
  try:
    ifx2stationname = config.get_var("base.stationname", None)
    if ifx2stationname is None:
      raise "influxdb2 stationname is not configured"
    ifx2host = config.get_var("influxdb2.host", None)
    if ifx2host is None:
      raise "influxdb2 host is not configured"
    ifx2port = config.get_var("influxdb2.port", None)
    if ifx2port is None:
      raise "influxdb2 port is not configured"
    ifx2org = config.get_var("influxdb2.org", None)
    if ifx2org is None:
      raise "influxdb2 org is not configured"
    ifx2apitoken = config.get_var("influxdb2.apitoken", None)
    if ifx2apitoken is None:
      raise "influxdb2 ApiKey is not configured"
    ifx2bucket = config.get_var("influxdb2.bucket", None)
    if ifx2bucket is None:
      raise "influxdb2 bucket is not configured"

    # connect database
    client = influxdb_client.InfluxDBClient(url=f'http://{ifx2host}:{ifx2port}', token=ifx2apitoken, org=ifx2org)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    # weatherdata = parsed_json_all['data']

    datapoint = (
      influxdb_client.Point("Weather")
      .tag("stationname", ifx2stationname)
      .field("time", weatherdata.time)  # Time from Weatherstation (not iso conform)
      .field("measurement", "Weather")

      .field("OutTemp", weatherdata.outtemp)
      .field("InTemp", weatherdata.intemp)
      .field("OutHumitity", weatherdata.outhumidity)
      .field("InHumidity", weatherdata.inhumidity)
      .field("Rain", weatherdata.rainrate)
      .field("Rain1h", weatherdata.rainhourly)
      .field("Rain24h", weatherdata.raindaily)
      .field("Pressure", weatherdata.pressureabs)
      .field("Wind", weatherdata.windspeed)
      # .field("WindAvg", float(weatherdata["wind"]["wind_speed"]["value"]) *1.60934)
      .field("WindGust", weatherdata.windgust)
      # .field("CL", 0)
      # .field("CT", 0)
      # .field("Status", parsed_json["qcStatus"])
      # .field("PNow", float(solar["Gesamtleistung_AC"]))
      .field("WindDir", weatherdata.winddirection)
    )

    log.debug(f"Return client.write_points(datapoint) is {write_api.write(bucket=ifx2bucket, org=ifx2org, record=datapoint)}")

    log.debug(f"Datapoint is: {datapoint}")
    log.info("Inserted InfluxDB2 dataset")
  except Exception as e:
    log.error("Error: " + str(e))


def set_weather_mqtt(weatherdata: WeatherData):
  try:
    mqtthost = config.get_var("mqtt.host")
    mqttport = config.get_var("mqtt.port", 1880)
    mqttid = config.get_var("mqtt.id", "weatherdata_" + str(time.time()))
    mqttuser = config.get_var("mqtt.user")
    mqttpassword = config.get_var("mqtt.password")
    mqttbasetopic = config.get_var("mqtt.basetopic")

    log.info("connecting to mqttbroker '{}' with client ID '{}'".format(mqtthost, mqttid))
    client = mqtt.Client(client_id=mqttid)
    client.username_pw_set(mqttuser, mqttpassword)

    client.enable_logger(log)
    client.connect(mqtthost, mqttport)

    client.loop_start()  # start the loop

    t = time.time()
    log.debug("Publishing message to topic '{}' with value '{}'".format(mqttbasetopic + "alive", t))
    client.publish(mqttbasetopic + "alive", t)

    log.debug("Publishing message to topic '{}' with value '{}'".format(mqttbasetopic + "data", jsons.dumps(parsed_json_all)))
    client.publish(mqttbasetopic + "data", jsons.dumps(weatherdata))

    client.loop_stop()  # stop the loop
    time.sleep(1)
    client.disconnect()

  except Exception as e:
     log.error(e)


def set_weather_log(weatherdata: WeatherData):
   print(jsons.dumps(weatherdata))
   log.info(jsons.dumps(weatherdata))


# Main program
try:
  inputservice = config.get_var("base.service_to_use", None)
  parsed_json_all = None
  if inputservice == "ecowitt":
    parsed_json_all = get_ecowitt_weather()
  elif inputservice == "weatherunderground":
    parsed_json_all = get_weatherunderground_weather()
  elif inputservice == "httpjson":
    parsed_json_all = get_http_weather()

  if parsed_json_all is None:
     raise Exception("No Data received")

  outputarray = config.get_var("base.output_to_use", None)
  for conf_output in outputarray:
    if conf_output == "influxdb":
       log.info("Output to influx")
       set_weather_influxdb(parsed_json_all)
    if conf_output == "influxdb2":
       log.info("Output to influx2")
       set_weather_influxdb2(parsed_json_all)
    if conf_output == "mqtt":
       log.info("Output to mqtt")
       set_weather_mqtt(parsed_json_all)
    if conf_output == "log":
       log.info("Output to log:")
       set_weather_log(parsed_json_all)
except Exception as e:
    log.error(e)

exit(0)
