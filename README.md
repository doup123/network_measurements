# TWPING Parsing & Storing in InfluxDB 

## Prerequisites
installed influxdb  
python influx client  

A testbed.py file that contains:  
influxdb_ip ="ip_address"  
infuxdb_port = port  
influxdb_username = "username"  
influxdb_passwd = "password"  
influxdb_db = "database_name"  

## Usage
Usage twping_measurement.py <src_ip> <dst_ip>  
python twping_measurement.py 10.1.3.100 10.1.1.100

## Tested
This is tested on Ubuntu 16.04.4 with X-Influxdb-Version: 0.10.0
