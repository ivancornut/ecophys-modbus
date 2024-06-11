from umodbus.serial import Serial as ModbusRTUMaster
from machine import Pin, I2C, SPI
import time, json
import urtc
import vfs
import sdcard

def error_data_string(nb=1):
    # this function is to fill the datatable if no
    # information is received from the device
    datafmted = ""
    for i in range(1,nb+1):
        datafmted = datafmted+","+str(999)
    return datafmted

time.sleep(5)
# Open the file containing parameters for this sensor node
with open('host.json') as f:
    read_data = f.read()


params = json.loads(read_data) # Parse the json file output

# Setup cs pin for SD SPI$
cs = Pin(17,Pin.OUT)
# setup SPI for the SD card
spi = machine.SPI(0,
                  baudrate=1000000,
                  polarity=0,
                  phase=0,
                  bits=8,
                  firstbit=machine.SPI.MSB,
                  sck=Pin(18),
                  mosi=Pin(19),
                  miso=Pin(16))
sd = sdcard.SDCard(spi, cs)
filsys = vfs.VfsFat(sd)

sleep_time = params["GENERAL"]["Time_Delta"]*60 * 1000 - 30*1000 # the Time during which the host should sleep (it leaves 1min for execution of tasks)
sleep_time_client_s = params["GENERAL"]["Time_Delta"]*60
sleep_time_minutes = params["GENERAL"]["Time_Delta"]

nb_clients = params["GENERAL"]["Client_nb"] # Count the number of clients and the number of values to retrieve per client
nb_values = [] # number of values per client
print(params)
for i in range(1, nb_clients+1):
     nb_values.append(params["CLIENT_"+str(i)]["nb_values"])
if len(nb_values) != nb_clients: print("Error on nb of clients") # check consistency

# Setup rtc to read it and save in data
i2c_clock = I2C(0,scl=Pin(5), sda=Pin(4))
rtc = urtc.PCF8523(i2c_clock)

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

    
    try:
        SD = True
        vfs.mount(filsys, "/sd")
        file = '/sd/data.txt'
    except:
        print("couldn't mount SD card")
        SD = False
        file = 'data.txt'
    while (rtc.datetime().minute % sleep_time_minutes) != 0:
        #this is the time at which data is retieved
        time.sleep(10)
    for i in range(1, nb_clients+1):
        try:
            host.write_single_register(slave_addr=i, register_address=250, register_value = sleep_time_client_s, signed = False)
        except:
            print("Could not set sleep time at client "+str(i))
    with open(file,'a') as f:
        for i in range(1,nb_clients+1):
            datetime = rtc.datetime()
            f.write(str(datetime.year)+","+str(datetime.month)+","+str(datetime.day)+","+str(datetime.hour)+","+str(datetime.minute)+","+str(datetime.second))
            f.write(","+str(i)) # write number of device in data file
            try:
                # Reading the holding registers of the client device
                # Starts at the starting address and until the starting address + register_qty
                print(nb_values[i-1])
                data = host.read_holding_registers(slave_addr=i, starting_addr=93, register_qty=nb_values[i-1])
                for d in data: # iterate over data array
                    f.write(","+str(d)) # write each value in csv file
                print("DateTime", str(datetime.minute))
                print('Value of Holding register 93: {}'.format(data)) # for debugging
                time.sleep(0.25)
                try:
                    # Putting device to sleep after succefull reading of sensor values
                    host.write_single_coil(slave_addr=i, output_address=123, output_value = 1)
                    print("Successfully set sleeping coil")
                except Exception as error:
                    print("Unsuccessful at setting sleepin coil")
                    print(error)
                led.off()
                f.write("\n") # prepare for next device
                time.sleep(0.25)
            except Exception as error:
                print("Problem with Client n°: "+str(i))
                print(error)
                f.write(error_data_string(nb=nb_values[i-1]) + "\n") # write false data
                led.on()
                time.sleep(0.25)
    if SD:
        vfs.umount("/sd")
    machine.lightsleep(sleep_time) # put host to sleep for an amount of time to save power
    #time.sleep(10)
    