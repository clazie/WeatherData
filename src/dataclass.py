#!/usr/bin/env python3

class WeatherData:
  time: str  # strftime('%Y-%m-%d %H:%M:%S')
  outtemp: float  # °C
  outfeelslike: float  # °C
  outapptemp: float  # °C
  outdrewpoint: float  # °C
  outhumidity: float  # %
  intemp: float  # °C
  inhumidity: float  # %
  solar: float  # w/m²
  uvi: float  # -
  rainrate: float  # mm/h
  rainevent: float  # mm
  rainhourly: float  # mm
  raindaily: float  # mm
  rainweekly: float  # mm
  rainmonthly: float  # mm
  rainyearly: float  # mm
  windspeed: float  # km/h
  windgust: float  # km/h
  winddirection: float  # °
  pressurerel: float  # hpa
  pressureabs: float  # hpa
  waterleak: float  # -
  battery_t_rh_p_sensor: float  # -
  battery_sensor_array: float  # -
