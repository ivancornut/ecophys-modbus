from umodbus.serial import Serial as ModbusRTUMaster
from machine import Pin
import time, json

# Open the file containing parameters for this sensor node
with open('host.json') as f:
	read_data = f.read()
# Parse the json file output
params = json.loads(read_data)

# Count the number of clients and the number of values to retrieve per client
nb_clients = params["GENERAL"]["Client_nb"]
nb_values = [] # number of values per client
for i in range(1, nb_clients+1):
     nb_values.append(params["ClIENT_"+str(i)]["nb_values"])
if len(nb_values) != nb_clients: print("Error on nb of clients")

# retrieve the UART Pins
rtu_pins = (Pin(params["GENERAL"]["RTU_Pins"][0]), Pin(params["GENERAL"]["RTU_Pins"][1]))
uart_id = params["GENERAL"]["UART_ID"]

led = Pin(25, Pin.OUT)

host = ModbusRTUMaster(
    pins = rtu_pins,
    baudrate = 9600,
    data_bits = 8,
    stop_bits = 1,
    parity = None,
    ctrl_pin = 12,
    uart_id = uart_id
    )

while True:
    for i in range(1,nb_clients+1):
        try:
            data = host.read_holding_registers(slave_addr=i, starting_addr=93, register_qty=nb_values[i])
            print('Value of Holding register 93: {}'.format(data))
            led.off()
            time.sleep(0.5)
        except:
            print("Problem with Client n°: "+str(i))
            led.on()
            time.sleep(0.5)
    time.sleep(5)
    