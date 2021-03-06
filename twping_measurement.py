import os,sys
from twping_parser import parse_twping
from influx_client import *
if len(sys.argv) < 3:
    print "Usage twping_measurement.py <src_ip> <dst_ip>"
else: 
    #src_ip="10.1.3.100"
    #dst_ip="10.1.1.100"
    src_ip = sys.argv[1]
    dst_ip = sys.argv[2]
    twping_results_file = "./twping_results_"+str(src_ip)+"_"+str(dst_ip)
    os.system("twping -c 20 -i 1 "+str(dst_ip)+" -c 10 >"+str(twping_results_file))
    twping_service=parse_twping(twping_results_file)
    influxdb_preprocess_write(twping_service,src_ip,dst_ip)
