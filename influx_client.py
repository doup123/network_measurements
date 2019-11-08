from influxdb import InfluxDBClient
from time import *
from testbed import *

def write_to_influx(measurements):
    client = InfluxDBClient(influxdb_ip, infuxdb_port, influxdb_username, influxdb_passwd, influxdb_db)
    client.write_points(measurements)

def influxdb_preprocess_write(twping_service,src_ip,dst_ip):

    json_body = [{
        "measurement": "test_twping",
        "tags": {"src_ip":src_ip, "dst_ip":dst_ip},
        "time": strftime("%Y-%m-%dT%H:%M:%S", gmtime(mktime(strptime(twping_service['time'], "%Y-%m-%dT%H:%M:%S.%f")[0:9]))),
        "fields": twping_service
    }]
    write_to_influx(json_body)
