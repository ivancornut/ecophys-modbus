from micropython import const
from umodbus.serial import ModbusRTU
from machine import Pin, I2C
from micropython_sht4x import sht4x
import time, onewire, ds18x20, math, json

ERROR_CODE = const(9999) # error code when sensor data cannot be read
REGISTER_HREG = const(93) # address of first register that contains the data
COIL = const(123) # address of the sleep coil

# Open the file containing parameters for this sensor node
with open('client.json') as f:
    read_data = f.read()

params = json.loads(read_data) # Parse the json file output
client_address = params["GENERAL"]["Client_ID"] # the client ID (its address on the ModBus network)
print("This is client nb "+str(client_address)) # for debugging
nb_unique_sensors = params["GENERAL"]["Unique_Sensors"] # The number of unique sensor types
sensor_types = params["UNIQUE_SENSOR_TYPES"]
if nb_unique_sensors != len(sensor_types): print("Error: Problem with sensor type number")

# Setting up the type and number of sensors
# For now only works with SHT45 and DS18B20 but can be expanded for other sensors
SHT45 = False 
if "SHT_45" in sensor_types:
    # Routine for extraction of information on present SHT45s
    SHT45 = True # Tells the device to read sht45s
    nb_SHT_45 = params["SHT_45"]["Nb"] # number of SHT45s
    print("There are " + str(nb_SHT_45) + " SHTs on this client") # debugging
    pins_sht45 = params["SHT_45"]["Sensor_Pins"] # get the I2C pins of the SHT45s
    if nb_SHT_45 != len(pins_sht45): print("Error: Problem with SHT45 number") # debugging
    i2c = []
    for i in pins_sht45:
        i2c.append(I2C(i["I2C"], sda = i["SDA"], scl = i["SCL"])) # Creating the I2C objects

DS18B20 = False
if "DS18B20" in sensor_types:
    # Routine for extraction of information on present DS18B20s
    DS18B20 = True # Tells the device to read DS18B20s
    nb_DS18B20 = params["DS18B20"]["Nb"] # Number of DS18B20s
    print("There are " + str(nb_DS18B20) + " DS18B20s on this client")
    addresses = params["DS18B20"]["adrss"] # The individual addresses of the DS18B20s
    if nb_DS18B20 != len(addresses): print("Error: Problem with DS18B20 number")
    ds_pin = Pin(params["DS18B20"]["Pin"]) # The GPIO pin on which DS18B20s are connected
    ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin)) # creating the ds object

led = Pin(25, Pin.OUT) # for debugging only

#def my_reg_set_cb(reg_type, address, val):
#    print('Custom callback, called on setting {} at {} to: {}'.format(reg_type, address, val))

def my_coil_set_cb(reg_type, address, val):
    """This function is to put the device to sleep following the retrieval of value by host
    while maintaining the decision of host on sleep (the host sets the coil to 0 for sleep"""
    if val==0:
        time.sleep(2) # we sleep after the information has been read
        # Since this is only a time.sleep it is for debugging purposes
        # machine.lightsleep() should be called for real world implementations
    else:
        print("No sleep") # in case something goes wrong

def my_reg_get_cb(reg_type, address, val):
    led.on() # for debugging
    values = ()
    print("Holding register is being read")
    if SHT45:
        for i in i2c: # do the loop on the number of SHT45 devices connected
            try:
                sht = sht4x.SHT4X(i) # initialize sh45 objects
                time.sleep(0.1) # give some time to device
                temperature, relative_humidity = sht.measurements # read sensor
                values.append(math.trunc(temperature*100), math.trunc(relative_humidity*100)) # write to register (x100 for floats to int)
            except:
                try: # in case measurement is impossible try resetting
                    sht = sht4x.SHT4X(i2c) # initialize sh45 objects
                    sht.reset() # soft reset the SHT45
                    time.sleep(0.1) # give some time to device
                    temperature, relative_humidity = sht.measurements # read sensor
                    values.append(math.trunc(temperature*100), math.trunc(relative_humidity*100)) # write to register (x100 for floats to int)
                except:
                    temperature = ERROR_CODE # if it goes wrong write 9999
                    relative_humidity = ERROR_CODE # if it goes wrong write 9999
                    values.append(math.trunc(temperature), math.trunc(relative_humidity)) # write to holding register so host device knows something is wrong
    if DS18B20: # Do the loop for number of DS18B20 connected (all on same pin since one-wire)
        ds_sensor.convert_temp() # function to tell sensors to start measurement routine
        time.sleep_ms(750) # time it takes sensors to read the temp
        for i in addresses:
            try:
                values.append(math.trunc(ds_sensor.read_temp(rom))*100) # reading values from sensor at address rom
            except:
                values.append(ERROR_CODE)
    client.set_hreg(address,values) # Put all values inside the holding registers
    print('Custom callback, called on getting {} at {}, currently: {}'.format(reg_type, address, val))
    led.off()

# Set the pins for UART communication
rtu_pins = (Pin(params["GENERAL"]["RTU_Pins"][0]), Pin(params["GENERAL"]["RTU_Pins"][1]))
uart_id = params["GENERAL"]["UART_ID"]

client = ModbusRTU( # Setup the ModBus object
    addr = client_address,
    pins = rtu_pins,
    baudrate = 9600, # important to keep consistent between host and client
    data_bits = 8, # important to keep consistent between host and client
    stop_bits = 1, # important to keep consistent between host and client
    parity = None, # important to keep consistent between host and client
    ctrl_pin = 12, # important to keep consistent between host and client
    uart_id = uart_id
    )

register_definitions = { # Setting up coils and registers
    "COILS": {"SLEEP_COIL": {"register": COIL,"len": 1,"val": 1, "on_get_cb": my_coil_set_cb}}, # coils give a status
    "HREGS": {"TEMPERATURE_and_HUM_HREG": {"register": REGISTER_HREG,"len": 2,"val": (9999,9999),"on_get_cb": my_reg_get_cb}}, # holding register for values
    "ISTS": {"EXAMPLE_ISTS": {"register": 67,"len": 1,"val": 0}},
    "IREGS": {"EXAMPLE_IREG": {"register": 10,"len": 1,"val": 60001}}
}

# use the defined values of each register type provided by register_definitions
client.setup_registers(registers=register_definitions)
while True:
    try:
        result = client.process()
    except KeyboardInterrupt:
        print('KeyboardInterrupt, stopping RTU client...')
        break
    except Exception as e:
        print('Exception during execution: {}'.format(e))