
#! /usr/bin/env python3

from pysnmp.hlapi import *
import time
from time import sleep
import sys
from influxdb import InfluxDBClient
from influx_client import *
from testbed import *
import logging
import threading
from time import sleep,strftime,strptime,gmtime,mktime
if len(sys.argv) < 8:
    
    print(
        "Usage python3 snmp_juniper_v2.py <source_ip> <destination_ip> <agent_type> <Community> <Owner> <test_name> <sleep_time_between_measurements>")
    sys.exit()
    
else:

    logging.basicConfig(level=logging.INFO, format=' %(asctime)s - %(levelname)s - %(message)s')

    #sys.argv = [sys.argv[0], '193.63.63.43', '193.63.63.44', 'TWAMP', 'public', 'c32', 't32', '60'] 


    def dateToString(myDate):
        year = str((myDate[0] * 256 + myDate[1])) + '-' + str(myDate[2]) + '-' + str(myDate[3]) + ', '
        hour = str(myDate[4]) + ':' + str(myDate[5]) + ':' + str(myDate[6])
        return year + hour

# Gloval varialbles
    results = {}
    # OID for juniper devices
    
    jnxTwampResSumDate = '1.3.6.1.4.1.2636.3.77.1.1.2.1.5'

    jnxRpmResSumDate = '1.3.6.1.4.1.2636.3.50.1.2.1.5'
    
    
    jnxTwampClientResultsCalculatedEntry = '1.3.6.1.4.1.2636.3.77.1.1.3.1'
    jnxRpmResultsCalculatedEntry =  '1.3.6.1.4.1.2636.3.50.1.3.1'

    # Table indexes:
    # Owner (ASCII)
    # TestName (ASCII)
    # SumCollection: 1 - currentTest, 2 - lastCompletedTest, 3 - movingAverage, 4 -allTests
    # CalSet: 1 - roundTripTime, 4 - egress delay, 7 - ingress delay

    Samples = '.2'
    Min = '.3'
    Max = '.4'
    Average = '.5'
    PktoPk = '.6'
    StdDev = '.7'
    Sum = '.8'

    Statistics = [Samples, Min, Max, Average, PktoPk, StdDev]
    StatisticsNames = ['Samples', 'Min', 'Max', 'Average', 'PktoPk', 'StdDev']



    # source ip -> sys.argv[1]
    # destination ip -> sys.argv[2]
    # agent_type  -> sys.argv[3]
    # Community -> sys.argv[4]
    # Owner (RPM) or control connection (TWAMP) -> sys.argv[5]
    # test_name (RPM) or test connection(TWAMP) -> sys.argv[6]
    # sleep time between measurements -> sys.argv[7]

    
    source_ip = sys.argv[1]
    destination_ip = sys.argv[2]
    agent_type = sys.argv[3]
    Community = sys.argv[4]
    Owner = sys.argv[5]
    TestName = sys.argv[6]
    sleep_time = sys.argv[7]
   
    if agent_type == 'RPM':
        SumDate = jnxRpmResSumDate
        CalculatedEntry = jnxRpmResultsCalculatedEntry
    elif agent_type == 'TWAMP':
        SumDate = jnxTwampResSumDate
        CalculatedEntry =  jnxTwampClientResultsCalculatedEntry
    else:
        print('agent_type specified as ' + agent_type + ' but it should be RPM or TWAMP')
        sys.exit()
        
    # constructing ASCII codes of Owner and TestName in Name



    Name = '.' + str(len(Owner)) + '.'
    for i in range(len(Owner)):
        Name = Name + str(ord(Owner[i])) + '.'

    Name = Name + str(len(TestName)) + '.'

    for i in range(len(TestName)):
        Name = Name + str(ord(TestName[i])) + '.'

    

    

    while True:
        # Obtaining date
        abc = ObjectIdentifier(SumDate + Name + '2')
        # print(abc)
        errorIndication, errorStatus, errorIndex, varBinds = next(
            getCmd(SnmpEngine(),
                   CommunityData(Community, mpModel=0),
                   UdpTransportTarget((source_ip, 161)),
                   ContextData(),
                   ObjectType(ObjectIdentity(abc)))
        )

        if errorIndication:
            print(errorIndication)

        elif errorStatus:
            print('%s at %s' % (errorStatus.prettyPrint(),
                                errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
        else:
            varBind = varBinds[0]
            SampleDate = dateToString(varBind[1])
            print()
            print('TestDate: ' + SampleDate)

        # adding the last two indexes
        # SumCollection = 2 lastCompletedTest
        # CalSet = 4 Egress delay, 7 Ingress delay
        metrics = {'roundTripTime': 1, 'posRttJitter': 2, 'negRttJitter': 3, 'egress': 4, 'posEgressJitter': 5,
                   'negEgresslJitter': 6, 'ingress': 7, 'posIngressJitter': 8, 'negIngressJitter': 9}

        # Obtaining Statistics
        print ()
        print ("Obtaining " + agent_type + " statistics")
        for k, v in metrics.items():
            i = 0
            print ()
            print ("Obtaining " + " " + agent_type + " " + str(k) + " statistics")
            oid = Name + '2.' + str(v)

            for s in Statistics:
                
                abc = ObjectIdentifier(CalculatedEntry + s + oid)
               
                
                errorIndication, errorStatus, errorIndex, varBinds = next(
                    getCmd(SnmpEngine(),
                           CommunityData(Community, mpModel=0),
                           UdpTransportTarget((source_ip, 161)),
                           ContextData(),
                           ObjectType(ObjectIdentity(abc)))
                )
                if errorIndication:
                    print('Error Indication' + errorIndication)

                elif errorStatus:
                    print ('Error Status')
                    print('%s at %s' % (errorStatus.prettyPrint(),
                                        errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
                else:
                    varBind = varBinds[0]
                    value = varBind[1]
                    print(k + StatisticsNames[i] + ' = ', str(value))
                    if StatisticsNames[i] == 'Samples':
                        results[k + StatisticsNames[i]] = str(value)
                    else:
                        results[k + StatisticsNames[i]] = str(value/1000.0)
                    
                    i = i + 1

        SampleDate = strftime("%Y-%m-%d %H:%M:%S",
             gmtime(mktime(strptime(SampleDate,
                                                    "%Y-%m-%d, %H:%M:%S"))))  
        json_body = [{
            "measurement": agent_type,
            "tags": {"src_ip": source_ip, "dst_ip": destination_ip},
            "time": SampleDate,
            "fields": results}]
        print('json body:')
        print(json_body)
        write_to_influx(json_body)
        sleep(int(sleep_time))
