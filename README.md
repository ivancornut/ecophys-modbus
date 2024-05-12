# Ecophys-Modbus
Using Pi Picos, RS485 and ModBus to create robust environmental networks tahta are able to operate in constrained conditions (low access to ressources, harsh climate, etc). 

## Objectives
We aim to build a low-cost, robust and resilient sensor network to characterize heterogeneous environments. In our case we work mainly in complex cocoa agroforestry systems in Central Africa (Cameroon). These systems are multi-layered and have a high diverity of shade and understory trees. In this context placing a few micro-environmental sensors is not sufficient to guarantee a good estimation of the effects of shade trees on the micro-evironment of cocoa trees.

## Network composition
### Host
The Host of our network is either a Pi Pico microcontroller with an adafruit datalogging shield or a RS-485 capable datalogger such as those provided by Campbell scientific. 
### Clients
Clients of the network are Pi Picos ([here](https://www.raspberrypi.com/products/raspberry-pi-pico/)) with a UART to RS-485 Grove module from Seed Studio ([here](https://wiki.seeedstudio.com/Grove-RS485/)). They are meant to consume the least power possible whilst still reading useful sensors by sleeping as much as possible.
### Sensors used in this project
#### Sensirion SHT45
The SHT45 from sensirion ([here](https://sensirion.com/products/catalog/SHT45/)) is a very accurate air temperature (+-0.1°C) and air humidity sensor (+-1%). This is largely sufficient for micro-climate assessment and is better than most commercially available air temp/hum sensors. It has the added benefit of having a heater to avoid creep in high humidity environments. It uses I2C as a communication protocol, there is already a micropython library available ([here](https://github.com/jposada202020/MicroPython_SHT4X/tree/master)) and we have easily developped a PCB and sensor casing design ([here](https://github.com/ivancornut/temp_hum_ecosols)).
#### DS18B20
