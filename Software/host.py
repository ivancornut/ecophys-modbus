from umodbus.serial import Serial as ModbusRTUMaster
from machine import Pin
import time

rtu_pins = (Pin(0), Pin(1))
uart_id = 0
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
    try:
        coil_status = host.read_holding_registers(slave_addr=10, starting_addr=93, register_qty=2)
        print('Status of coil 123: {}'.format(coil_status))
        led.off()
    except:
        led.on()
    time.sleep(5)
    