[EcoWitt Doku](https://doc.ecowitt.net/web/#/apiv3en?page_id=17)

## Beispiel
Aktuelle Daten
`https://api.ecowitt.net/api/v3/device/real_time?application_key=09639029E36E8CFEAE9979935D638BCD&api_key=5e3c78ba-25a7-4f03-9de4-6b7677267ea8&mac=98:CD:AC:32:3D:3D&call_back=all`

#### Json Antwort
```json
{
    "code": 0,
    "msg": "success",
    "time": "1643877904",
    "data": {
        "outdoor": {
            "temperature": {
                "time": "1643877861",
                "unit": "ºF",
                "value": "40.1"
            },
            "feels_like": {
                "time": "1643877861",
                "unit": "ºF",
                "value": "40.1"
            },
            "dew_point": {
                "time": "1643877861",
                "unit": "ºF",
                "value": "39.1"
            },
            "humidity": {
                "time": "1643877861",
                "unit": "%",
                "value": "96"
            }
        },
        "indoor": {
            "temperature": {
                "time": "1643877861",
                "unit": "ºF",
                "value": "73.4"
            },
            "humidity": {
                "time": "1643877861",
                "unit": "%",
                "value": "40"
            }
        },
        "solar_and_uvi": {
            "solar": {
                "time": "1643877861",
                "unit": "w\/m^2",
                "value": "34.8"
            },
            "uvi": {
                "time": "1643877861",
                "unit": "",
                "value": "0"
            }
        },
        "rainfall": {
            "rain_rate": {
                "time": "1643877861",
                "unit": "in\/hr",
                "value": "0.00"
            },
            "daily": {
                "time": "1643877861",
                "unit": "in",
                "value": "0.00"
            },
            "event": {
                "time": "1643877861",
                "unit": "in",
                "value": "0.00"
            },
            "hourly": {
                "time": "1643877861",
                "unit": "in",
                "value": "0.00"
            },
            "weekly": {
                "time": "1643877861",
                "unit": "in",
                "value": "0.05"
            },
            "monthly": {
                "time": "1643877861",
                "unit": "in",
                "value": "0.05"
            },
            "yearly": {
                "time": "1643877861",
                "unit": "in",
                "value": "0.05"
            }
        },
        "wind": {
            "wind_speed": {
                "time": "1643877861",
                "unit": "mph",
                "value": "0.0"
            },
            "wind_gust": {
                "time": "1643877861",
                "unit": "mph",
                "value": "1.1"
            },
            "wind_direction": {
                "time": "1643877861",
                "unit": "º",
                "value": "135"
            }
        },
        "pressure": {
            "relative": {
                "time": "1643877861",
                "unit": "inHg",
                "value": "30.08"
            },
            "absolute": {
                "time": "1643877861",
                "unit": "inHg",
                "value": "29.31"
            }
        },
        "batt": {
            "t_rh_p_sensor": {
                "time": "1643877861",
                "unit": "",
                "value": "0"
            },
            "ws65_67_69_sensor": {
                "time": "1643877861",
                "unit": "",
                "value": "0"
            }
        }
    }
}

```

## Zyklisches holen der Daten

### Bash Skript

```bash
#!/bin/bash
python3.7 /home/pi/wetter/ecowitt2influxdb.py
exit 0
```

### crontab
Mit 
```
sudo crontab -e
```
die crontab Datei für den Benutzer `root`zum editieren öffnen
und die folgende Zeile hinzufügen
```ini
* * * * * /home/pi/wetter/wetterupdate.sh
```
Damit werden jede Minute die Daten wom ecowitt Server geholt und in die InfluxDB eingetragen.