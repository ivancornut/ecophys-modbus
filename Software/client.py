from micropython import const
from umodbus.serial import ModbusRTU
from machine import Pin, I2C
from micropython_sht4x import sht4x
import time
import math

i2c = I2C(1, sda=Pin(14), scl=Pin(15)) # Setting the pins for SHT45
led = Pin(25, Pin.OUT)

CLIENT_ADDRESS = const(1)
ERROR_CODE = const(999)
REGISTER_HREG = const(93)
COIL = const(123)

def my_reg_set_cb(reg_type, address, val):
    print('Custom callback, called on setting {} at {} to: {}'.format(reg_type, address, val))

def my_coil_set_cb(reg_type, address, val):
    """This function is to put the device to sleep following the retrieval of value by host
    while maintaining the decision of host on sleep (the host sets the coil to 0 for sleep"""
    if val==0:
        time.sleep(2) # we sleep after the information has been read
    else:
        print("No sleep") # in case something goes wrong

def my_reg_get_cb(reg_type, address, val):
    led.on()
    try:
        sht = sht4x.SHT4X(i2c)
        #sht.reset()
        time.sleep(0.1)
        temperature, relative_humidity = sht.measurements
    except:
        try:
            sht = sht4x.SHT4X(i2c)
            sht.reset()
            time.sleep(0.1)
            temperature, relative_humidity = sht.measurements
        except:
            temperature = ERROR_CODE
            relative_humidity = ERROR_CODE
    client.set_hreg(address,(math.trunc(temperature),math.trunc(relative_humidity)))
    print('Custom callback, called on getting {} at {}, currently: {}'.format(reg_type, address, val))
    led.off()
#i2c = I2C(1, sda=Pin(14), scl=Pin(15), freq=400000)  # Correct I2C pins for RP2040
# Set the pins for communication
rtu_pins = (Pin(0), Pin(1))
uart_id = 0 # the corresponding ID for the uart

client = ModbusRTU(
    addr = CLIENT_ADDRESS,
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