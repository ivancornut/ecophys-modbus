from umodbus.serial import Serial as ModbusRTUMaster
from machine import Pin
import time, json

# Open the file containing parameters for this sensor node
with open('host.json') as f:
    read_data = f.read()

params = json.loads(read_data) # Parse the json file output

sleep_time = params["GENERAL"]["Time_Delta"]*60 * 1000 - 60*1000 # the Time during which the host should sleep (it leaves 1min for execution of tasks)

nb_clients = params["GENERAL"]["Client_nb"] # Count the number of clients and the number of values to retrieve per client
nb_values = [] # number of values per client
print(params)
for i in range(1, nb_clients+1):
     nb_values.append(params["CLIENT_"+str(i)]["nb_values"])
if len(nb_values) != nb_clients: print("Error on nb of clients") # check consistency

# retrieve the UART Pins
rtu_pins = (Pin(params["GENERAL"]["RTU_Pins"][0]), Pin(params["GENERAL"]["RTU_Pins"][1])) # the GPIO pins
uart_id = params["GENERAL"]["UART_ID"] # The UART ID, see Pico Pinout

led = Pin(25, Pin.OUT)

host = ModbusRTUMaster( # setup the Modbus object
    pins = rtu_pins,
    baudrate = 9600, # important to keep consistent between host and client
    data_bits = 8, # important to keep consistent between host and client
    stop_bits = 1, # important to keep consistent between host and client
    parity = None, # important to keep consistent between host and client
    ctrl_pin = 12, # important to keep consistent between host and client
    uart_id = uart_id
    )

while True:
    with open('data.txt','a') as f:
        for i in range(1,nb_clients+1):
            f.write(str(i)) # write number of device in data file
            try:
                # Reading the holding registers of the client device
                # Starts at the starting address and until the starting address + register_qty
                data = host.read_holding_registers(slave_addr=i, starting_addr=93, register_qty=nb_values[i])
                for d in data: # iterate over data array
                    f.write(","+str(d)) # write each value in csv file
                print('Value of Holding register 93: {}'.format(data)) # for debugging
                try:
                    # Putting device to sleep after succefull reading of sensor values
                    host.write_single_coil(slave_addr=i, output_address=123, output_value = 0)
                    print("Successfully set sleeping coil")
                except:
                    print("Unsuccessful at setting sleepin coil")
                led.off()
                f.write("\n") # prepare for next device
                time.sleep(0.25)
            except:
                print("Problem with Client n°: "+str(i))
                f.write(",1,1,1" + "\n") # write false data
                led.on()
                time.sleep(0.25)
    machine.lightsleep(sleep_time) # put host to sleep for an amount of time to save power
    