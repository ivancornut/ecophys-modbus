echo "Time on the device before setting:"
mpremote run read_rtc_time.py
echo "Setting time on device..."
mpremote rtc --set
mpremote run set_rtc_time.py
echo "Time on the device after setting:"
mpremote run read_rtc_time.py
echo "Downloading data file to current directory"
mpremote connect auto run read_sd.py fs cp :sd/data.txt data.txt

