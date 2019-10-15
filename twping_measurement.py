import os
from twping_parser import parse_twping
from influx_client import *
src_ip="10.1.3.100"
dst_ip="10.1.1.100"
twping_results_file = "./twping_results"
os.system("twping "+str(dst_ip)+">"+str(twping_results_file))
twping_service=parse_twping(twping_results_file)
influxdb_preprocess_write(twping_service,src_ip,dst_ip)