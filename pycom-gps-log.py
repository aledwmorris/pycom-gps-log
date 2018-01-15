## pycom-gps-log.py
## (C) Copyright 2018 Aled Morris
## Distribution permitted per the Modified BSD License

## simple LoRaWAN GPS coverage logger for LoPy with PyTrack
## desigmed to work with http://map.thethings.nyc/
## upload this file to your LoPy as 'main.py'

import pycom
from utime import sleep,sleep_ms
from L76GNSS import L76GNSS
from pytrack import Pytrack
from network import LoRa
from binascii import unhexlify
import socket

####
## obtain your own app key based on your device MAC (DevEUI)
####

## my test app
##app_eui = unhexlify('70B3D57ED0009494')
##app_key = unhexlify('3FBE684796A5142E2050620A4F297D34')

## map.thethings.nyc
app_eui = unhexlify('70B3D57EF0001C38')
app_key = unhexlify('8EE9FA823F2DB5B68571A59D492242B0')

l76 = None
lora = None

def setup():
  global l76,lora
  if pycom.wifi_on_boot():      ## attempt to save battery
    pycom.wifi_on_boot(False)
  pycom.heartbeat(False)
  py = Pytrack()
  l76 = L76GNSS(py, timeout=30)
  lora = LoRa(mode=LoRa.LORAWAN)
  ## print('LoRa MAC %s' % binascii.hexlify(lora.mac()))

lora_socket = None

def join_lorawan():
  global lora_socket
  while not lora.has_joined():
    ## print('Joining...')
    lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key), timeout=0)
    count = 0
    while (not lora.has_joined()) and count < 300: ## wait one minute
      pycom.rgbled(0x000a0a if count&1 else 0)     ## LED flashing while joining
      sleep_ms(200)
      count += 1
  pycom.rgbled(0)
  lora_socket = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
  lora_socket.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)  ## data rate 5 = SF7 127kbps
  lora_socket.setblocking(True)

# from http://map.thethings.nyc/
# Data: Send lat/lon in 7 byte packetspycom.rgbled(0 with the structure
#  Byte 00: Format indicator. 0x01
#  Byte 01-03: Latitude encoding. Little endian integer. encoding = (latitude * 93206.0)
#  Byte 04-06: Longitude encoding. Little endian integer. encoding = (longitude * 46603.0)

# this packet is recycled to save memory churn
data_packet = bytearray(9)

def upload_data(latlon):
  lat = int(latlon[0] * 93206.0)
  lon = int(latlon[1] * 46603.0)
  data_packet[0] = 0x01
  data_packet[1] = lat&0xff
  data_packet[2] = (lat>>8)&0xff
  data_packet[3] = (lat>>16)&0xff
  data_packet[4] = (lat>>24)&0xff
  data_packet[5] = lon&0xff
  data_packet[6] = (lon>>8)&0xff
  data_packet[7] = (lon>>16)&0xff
  data_packet[8] = (lon>>24)&0xff
  lora_socket.send(data_packet)
  pycom.rgbled(0x008000)  ## green = data uploaded

last_lat = 0
last_lon = 0

def loop():
  global last_lat,last_lon
  latlon = l76.coordinates()
  ## print('lat=%f lon=%f' % (latlon[0], latlon[1]))
  if latlon == (None, None):
    pycom.rgbled(0x800000)  ## red = no gps lock
  else:
    pycom.rgbled(0x000080)  ## blue = got gps, maybe uploading data
    ## threshold of 0.001 degrees represents about 100m of distance
    if abs(last_lat - latlon[0]) > 0.001 or abs(last_lon - latlon[1]) > 0.001:
      upload_data(latlon)
      last_lat = latlon[0]
      last_lon = latlon[1]

def main():
  setup()
  while True:
    ## print('loop...')
    if not lora.has_joined():
      join_lorawan()
    loop()
    sleep(1)        ## leave LED on for a second
    pycom.rgbled(0) ## LED off
    sleep(29)       ## half a minute between polls to preserve battery

if __name__ == "__main__":
  main()
