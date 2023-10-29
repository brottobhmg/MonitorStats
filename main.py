import json
import time
import psutil
import platform
import cpuinfo
import socket
import uuid
import re
import GPUtil
import os
import influxdb_client
from influxdb_client import Point
from influxdb_client.client.write_api import SYNCHRONOUS




pcName="pcName"
org = "org"
url = "http://pi:8086"
bucket="bucket"
#--------------------------------------
token = os.environ.get("INFLUXDB_TOKEN")
system={}


def toMB(bytes, suffix="B"):
    """
    Scale bytes to its proper format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return float(f"{bytes:.2f}")#{unit}{suffix}"
        bytes /= factor





def getAllInfo():
    uname = platform.uname()
    system["system"]=uname.system
    system["pc_name"]=uname.node
    system["release"]=uname.release
    system["version"]=uname.version
    system["machine"]=uname.machine
    system["processor"]=cpuinfo.get_cpu_info()['brand_raw']
    system["ip_address"]=socket.gethostbyname(socket.gethostname())
    system["mac_address"]=':'.join(re.findall('..', '%012x' % uuid.getnode()))

    cpu={}
    cpufreq = psutil.cpu_freq()
    cpu["cpu_physical_cores"]=psutil.cpu_count(logical=False)
    cpu["cpu_total_cores"]=psutil.cpu_count(logical=True)
    cpu["cpu_max_frequency"]=int(cpufreq.max)
    cpu["cpu_total_usage"]=psutil.cpu_percent()
    system["cpu"]=cpu

    memory={}
    svmem = psutil.virtual_memory()
    memory["ram_total"]= toMB(svmem.total)
    memory["ram_available"]= toMB(svmem.available)
    memory["ram_used"]= toMB(svmem.used)
    memory["ram_percentage"]= svmem.percent
    system["ram"]=memory

    disk={}
    partitions = psutil.disk_partitions()
    for partition in partitions:
        if partition.device=="C:\\" or partition.device=="/dev/root":
            #print(f"=== Device: {partition.device} ===")
            try:
                partition_usage = psutil.disk_usage(partition.mountpoint)
            except PermissionError:
                # this can be catched due to the disk that
                # isn't ready
                continue
            disk["disk_total_size"]=toMB(partition_usage.total)
            disk["disk_used"]= toMB(partition_usage.used)
            disk["disk_free"]= toMB(partition_usage.free)
            disk["disk_percentage"]= partition_usage.percent
    system["disk_main"]=disk

    gpus=[]
    devices = GPUtil.getGPUs()
    for i,device in enumerate(devices):    
        info={}
        info["gpu_uuid_"+str(i)]=device.uuid
        info["gpu_name_"+str(i)]=device.name
        info["gpu_load_"+str(i)]=device.load*100
        info["gpu_memory_usage_"+str(i)]=round(device.memoryUtil*100,1)
        info["gpu_memory_total_"+str(i)]=str(device.memoryTotal)
        info["gpu_memory_used_"+str(i)]=device.memoryUsed
        info["gpu_memory_free_"+str(i)]=device.memoryFree
        info["gpu_driver_version_"+str(i)]=device.driver
        info["gpu_display_mode_"+str(i)]=device.display_mode
        info["gpu_display_active_"+str(i)]=device.display_active
        info["gpu_temperature_"+str(i)]=device.temperature
        info["gpu_serial_"+str(i)]=device.serial
        info["gpu_core_clock_"+str(i)]=device.core_clock
        info["gpu_memory_clock_"+str(i)]=device.memory_clock
        info["gpu_vbios_version_"+str(i)]=device.vbios_version
        info["gpu_fan_speed_"+str(i)]=device.fan_speed
        info["gpu_power_draw_"+str(i)]=device.power_draw
        info["gpu_power_limit_"+str(i)]=str(device.power_limit)
        gpus.append(info)
    system["gpus"]=gpus


def toInfluxdb():
    data=system
    write_client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
    write_api = write_client.write_api(write_options=SYNCHRONOUS)
    point = Point("misurazione")
    point.tag("source", pcName)
    for x in data.items():
        if type(x[1])==str:
            #print(x[0]+" ==> "+x[1])
            point.field(x[0],x[1])
        elif type(x[1])==dict:
            for a in x[1]: #a:key, x[1][a]:value
                #print(a+" ==> "+x[1][a])
                point.field(a,x[1][a])
        elif type(x[1])==list:
            for gpu in x[1]: #x[1]: gpus array
                for a in gpu:
                    #print(a+" ==> "+gpu[a])
                    point.field(a,gpu[a])

    write_api.write(bucket=bucket, org=org, record=point)



while True:
    start=time.time()
    getAllInfo()
    #with open("log.json","w") as f:
    #    f.write(json.dumps(system))
    toInfluxdb()
    print("Took "+str(round((time.time()-start)*1000,0))+" ms")
    time.sleep(60)
