# Ecophys-Modbus
Using Pi Picos, RS485 and ModBus to create robust environmental networks tahta are able to operate in constrained conditions (low access to ressources, harsh climate, etc). 

## Objectives
We aim to build a low-cost, robust and resilient sensor network to characterize heterogeneous environments. In our case we work mainly in complex cocoa agroforestry systems in Central Africa (Cameroon). These systems are multi-layered and have a high diverity of shade and understory trees. In this context placing a few micro-environmental sensors is not sufficient to guarantee a good estimation of the effects of shade trees on the micro-evironment of cocoa trees.

## Network hardware composition
### Host
The Host of our network is either a Pi Pico microcontroller with an adafruit datalogging shield or a RS-485 capable datalogger such as those provided by Campbell scientific. 
### Clients
Clients of the network are Pi Picos ([here](https://www.raspberrypi.com/products/raspberry-pi-pico/)) with a UART to RS-485 Grove module from Seed Studio ([here](https://wiki.seeedstudio.com/Grove-RS485/)). They are meant to consume the least power possible whilst still reading useful sensors by sleeping as much as possible.
### Cable
For the clients and the host to communicate we need to used a cable that is cable of transporting: power to the devices, A line of RS-485, B line of RS-485 and GND. We found that the most adapted cable for this use was the RJ45 cable. It is readily availble in Cameroon and has a total of 4 twisted pairs. One twisted pair is for A and B lines of RS485, one twisted pair is for +3V and one twisted pair + external shielding is for GND.
### Interconnection
For the interconnections at each node we will use 3-way wago connectors, one for each (+V, GND, A, B). 
### Sensors used in this project
#### Sensirion SHT45
The SHT45 from sensirion ([here](https://sensirion.com/products/catalog/SHT45/)) is a very accurate air temperature (+-0.1°C) and air humidity sensor (+-1%). This is largely sufficient for micro-climate assessment and is better than most commercially available air temp/hum sensors. It has the added benefit of having a heater to avoid creep in high humidity environments. It uses I2C as a communication protocol, there is already a micropython library available ([here](https://github.com/jposada202020/MicroPython_SHT4X/tree/master)) and we have easily developped a PCB and sensor casing design ([here](https://github.com/ivancornut/temp_hum_ecosols)).
#### DS18B20
The DS18B20 from Analog devices ([here](https://www.analog.com/en/products/ds18b20.html)) is a one-wire temperature sensor with an accuracy of +-0.5°C out of the box. There is often an issue with forged sensors but this can be avoided by sourcing this sensor at reputable vendors. The accuracy of genuine DS18B20 is often better than 0.5°C (personnal observation). Its main adavantages are its physical format (TO-92), the use of one-wire protocol, implementation in base micropython and its low-drift ([here](https://www.mdpi.com/2673-4591/10/1/56)). It will be used mainly for soil temperature. In the future it could advantagily be replaced by the MAX30207 ([here](https://www.analog.com/en/products/max30207.html) that has +- 0.1°C accuracy. 
#### ADS1106
This sensor is a 16-bit ADC that we use to measure the output of a linear potentiometer leveraged in our dendrometer (here). It uses the I2C protocol to communicate and has an already developped micropython library ([here](https://github.com/robert-hh/ads1x15)). There are several modules that make this IC readily usable.
