# MonitorStats
Collect data from PCs with Python, save into InfluxDB and visualize with Grafana using Raspberry Pi


## Requirements
- Raspberry Pi
  * [InfluxDB](https://www.influxdata.com/)
  * [Grafana](https://grafana.com/)
- [Python](https://www.python.org/) on the PC to retrieve the data

You can run the Python script on the Raspberry Pi or on other PCs.

### Python dependecies
- json
- time
- psutil
- platform
- py-cpuinfo
- socket
- uuid
- re
- [GPUtil](https://github.com/brottobhmg/gputil.git) (my fork)
- influxdb_client
- os


## My stuff
Tested with:
- Raspberry Pi 4B 8GB with OS 64bit
- Pc Windows10 with Nviadia gpu(s)
- Grafana version 10.2.0
- InfluxDB version 2.7.3
- Python >= 3.9.2


## How to
- Install [InfluxDB](https://randomnerdtutorials.com/install-influxdb-2-raspberry-pi/) on Raspberry
- Install [Grafana](https://grafana.com/tutorials/install-grafana-on-raspberry-pi/) on Raspberry
- You need to fill some data into Python file:
  * 'pcName' : alias of the pc that are sending the information
  * 'org' : name of your organization in InfluxDB
  * 'url' : the url of your Raspberry in the LAN
  * 'bucket' : name of the destination bucket in InfluxDB to save all information 
- Retrieve a "All Access API Token" on InfluxDB and [set it](https://www.twilio.com/blog/how-to-set-environment-variables-html) as environment variable














