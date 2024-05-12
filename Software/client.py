from micropython import const
from umodbus.serial import ModbusRTU
from machine import Pin, I2C
from micropython_sht4x import sht4x
import time, onewire, ds18x20, math, json

ERROR_CODE = const(9999)
REGISTER_HREG = const(93)
COIL = const(123)

SHT45 = False
DS18B20 = False

# Open the file containing parameters for this sensor node
with open('client.json') as f:
    read_data = f.read()

# Parse the json file output
params = json.loads(read_data)
client_address = params["GENERAL"]["Client_ID"]
print("This is client nb "+str(client_address))
nb_unique_sensors = params["GENERAL"]["Unique_Sensors"]
sensor_types = params["UNIQUE_SENSOR_TYPES"]
if nb_unique_sensors != len(sensor_types): print("Error: Problem with sensor type number")

# For now only works with SHT45 and DS18B20 but can be expanded for other sensors
if "SHT_45" in sensor_types:
    # Routine for extraction of information on present SHT45s
    SHT45 = True
    nb_SHT_45 = params["SHT_45"]["Nb"]
    print("There are " + str(nb_SHT_45) + " SHTs on this client")
    pins_sht45 = params["SHT_45"]["Sensor_Pins"]
    if nb_SHT_45 != len(pins_sht45): print("Error: Problem with SHT45 number")
    i2c = []
    for i in pins_sht45:
        i2c.append(I2C(i["I2C"], sda = i["SDA"], scl = i["SCL"])) # Inititalising I2C connection 

if "DS18B20" in sensor_types:
    # Routine for extraction of information on present DS18B20s
    DS18B20 = True
    nb_DS18B20 = params["DS18B20"]["Nb"]
    print("There are " + str(nb_DS18B20) + " DS18B20s on this client")
    addresses = params["DS18B20"]["adrss"]
    if nb_DS18B20 != len(addresses): print("Error: Problem with DS18B20 number")
    ds_pin = Pin(params["DS18B20"]["Pin"])
    ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))

led = Pin(25, Pin.OUT) # for debugging only

def my_reg_set_cb(reg_type, address, val):
    print('Custom callback, called on setting {} at {} to: {}'.format(reg_type, address, val))

def my_coil_set_cb(reg_type, address, val):
    """This function is to put the device to sleep following the retrieval of value by host
    while maintaining the decision of host on sleep (the host sets the coil to 0 for sleep"""
    if val==0:
        time.sleep(2) # we sleep after the information has been read
        # Since this is only a time.sleep it is for debugging purposes
    else:
        print("No sleep") # in case something goes wrong

def my_reg_get_cb(reg_type, address, val):
    led.on()
    values = ()
    print("Holding register is being read")
    if SHT45:
        for i in i2c: # do the loop on the number of SHT45 devices connected
            try:
                sht = sht4x.SHT4X(i)
                time.sleep(0.1)
                temperature, relative_humidity = sht.measurements
                values.append(math.trunc(temperature*100), math.trunc(relative_humidity*100))
            except:
                try:
                    sht = sht4x.SHT4X(i2c)
                    sht.reset()
                    time.sleep(0.1)
                    temperature, relative_humidity = sht.measurements
                    values.append(math.trunc(temperature*100), math.trunc(relative_humidity*100))
                except:
                    temperature = ERROR_CODE
                    relative_humidity = ERROR_CODE
                    values.append(math.trunc(temperature), math.trunc(relative_humidity))
    if DS18B20: # Do the loop for number of DS18B20 connected (all on same pin since one-wire)
        ds_sensor.convert_temp()
        time.sleep_ms(750)
        for i in addresses:
            try:
                values.append(math.trunc(ds_sensor.read_temp(rom))*100)
            except:
                values.append(ERROR_CODE)
    client.set_hreg(address,values)
    print('Custom callback, called on getting {} at {}, currently: {}'.format(reg_type, address, val))
    led.off()

# Set the pins for communication
rtu_pins = (Pin(params["GENERAL"]["RTU_Pins"][0]), Pin(params["GENERAL"]["RTU_Pins"][1]))
uart_id = params["GENERAL"]["UART_ID"]

client = ModbusRTU(
    addr = client_address,
    pins = rtu_pins,
    baudrate = 9600,
    data_bits = 8,
    stop_bits = 1,
    parity = None,
    ctrl_pin = 12,
    uart_id = uart_id
    )

register_definitions = {
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