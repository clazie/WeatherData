
# SolarPy

![Python application](https://github.com/cszielke/SolarPy/workflows/Python%20application/badge.svg) [![Documentation Status](https://readthedocs.org/projects/solarpy/badge/?version=latest)](https://solarpy.readthedocs.io/en/latest/?badge=latest)

![Logo](./docs/img/favicon256.png "Logo")

## Datenerfassung für Solaranlage mit Fronius Wechselrichter und Fronius IG Interface Card/Box

Das Programm ist gedacht, um mittels eines Raspberry Pi's die Daten der Wechselrichter über das interne Netzwerk zur Verfügung zu stellen. Es kann aber im Prinzip jeder Rechner -ob Linux oder Windows - verwendet werden.

Es besteht die Möglichkeit die Daten in einer MySQL und/oder InfluxDB Datenbank zu archivieren.

Über eine REST-API Schnittstelle oder über MQTT können die Daten abgefragt werden. Andere Ein-/Ausgabeschnittstellen sind leicht implementierbar.

Das Programm ist komplett in Python geschrieben und benötigt keine Oberfläche. Das Programm lässt sich umfangreich über eine CFG-Datei konfigurieren.

## Dokumentation

Die Dokumentation für dieses Projekt kann unter [Doku](https://cszielke.github.io/SolarPy/) gefunden werden..
