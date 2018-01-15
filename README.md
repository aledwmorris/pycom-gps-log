# pycom-gps-log
GPS logger for LoRaWAN using PyCom LoPy and PyTrack, mapping at http://map.thethings.nyc/

If you want to test against your own application in The Things Network you can use this data decoder:

```javascript
function Decoder(bytes, port) {
  var decoded = {};
  if (bytes[0] == 0x01) {
    decoded.lat = (bytes[1] | bytes[2]<<8 | bytes[3]<<16 | bytes[4]<<24)/93206.0;
    decoded.lon = (bytes[5] | bytes[6]<<8 | bytes[7]<<16 | bytes[8]<<24)/46603.0;
  }
  return decoded;
}
```

## Links
* https://pycom.io/product/lopy/
* https://pycom.io/product/pytrack/

## LED status
* flashing cyan = connecting to LoRaWAN
* red = no gps lock
* blue = got gps, will upload if moved
* green = uploaded
