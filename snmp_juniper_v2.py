
#! /usr/bin/env python3.5

from pysnmp.hlapi import *
import time
from time import sleep
import sys
# from influxdb import InfluxDBClient
from influx_client import *
# from testbed import *
import logging
import threading

if len(sys.argv) < 6:
    print(
        "Usage python3 snmp_juniper_v2.py <source_ip> <destination_ip> <control_connection> <test_connection> <sleep_time_between_measurements>")
else:

    logging.basicConfig(level=logging.INFO, format=' %(asctime)s - %(levelname)s - %(message)s')


    def dateToString(myDate):
        year = str((myDate[0] * 256 + myDate[1])) + '-' + str(myDate[2]) + '-' + str(myDate[3]) + ', '
        hour = str(myDate[4]) + ':' + str(myDate[5]) + ':' + str(myDate[6])
        return year + hour


    # source ip -> sys.argv[1]
    # destination ip -> sys.argv[2]
    # owner (control connection) -> sys.argv[3]
    # test (test connection) -> sys.argv[4]
    # sleep time between measurements -> sys.argv[5]

    source_ip = sys.argv[1]
    destination_ip = sys.argv[2]
    control_connection = sys.argv[3]
    test_connection = sys.argv[4]
    sleep_time = sys.argv[5]
    # Gloval varialbles
    results = {}
    # OID for juniper devices
    jnxTwampClientResultsSampleEntry = ObjectIdentifier('1.3.6.1.4.1.2636.3.77.1.1.1.1')
    jnxTwampResSampleValue = ObjectIdentifier('1.3.6.1.4.1.2636.3.77.1.1.1.1.2')
    jnxTwampResSampleDate = ObjectIdentifier('1.3.6.1.4.1.2636.3.77.1.1.1.1.3')
    jnxTwampResSumDate = '1.3.6.1.4.1.2636.3.77.1.1.2.1.5'
    # Calc table
    jnxTwampClientResultsCalculatedEntry = '1.3.6.1.4.1.2636.3.77.1.1.3.1'

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

    Owner = control_connection
    TestName = test_connection

    # Owner = 'c24'
    # TestName = 't24'

    # constructing ASCII codes of Owner and TestName in Name
    Name = '.' + str(len(Owner)) + '.'
    for i in range(len(Owner)):
        Name = Name + str(ord(Owner[i])) + '.'

    Name = Name + str(len(TestName)) + '.'

    for i in range(len(TestName)):
        Name = Name + str(ord(TestName[i])) + '.'

    # print ('Owner.TestName: ', Name)

    while True:
        # Obtaining date
        abc = ObjectIdentifier(jnxTwampResSumDate + Name + '2')
        # print(abc)
        errorIndication, errorStatus, errorIndex, varBinds = next(
            getCmd(SnmpEngine(),
                   CommunityData('public', mpModel=0),
                   UdpTransportTarget(('172.16.0.194', 161)),
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
            print('TestDate: ' + SampleDate)

        # adding the last two indexes
        # SumCollection = 2 lastCompletedTest
        # CalSet = 4 Egress delay, 7 Ingress delay
        metrics = {'roundTripTime': 1, 'rttJitter': 2, 'rttInterarrivalJitter': 3, 'egress': 4, 'egressJitter': 5,
                   'egressInterarrivalJitter': 6, 'ingress': 7, 'ingressJitter': 8, 'ingressInterarrivalJitter': 9}

        # Obtaining Statistics
        print ("Obtaining  statistics")
        for k, v in metrics.items():
            i = 0
            print ("Obtaining " + str(k) + " statistics")
            oid = Name + '2.' + str(v)
            for s in Statistics:
                #    print('s= ', s)
                abc = ObjectIdentifier(jnxTwampClientResultsCalculatedEntry + s + oid)
                #    print('Object ID = ' + str(abc))
                errorIndication, errorStatus, errorIndex, varBinds = next(
                    getCmd(SnmpEngine(),
                           CommunityData('public', mpModel=0),
                           UdpTransportTarget(('172.16.0.194', 161)),
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
                    value = varBind[1]
                    # print(k + StatisticsNames[i] + ' = ', str(value))
                    results[k + StatisticsNames[i]] = str(value/1000.0)
                    i = i + 1

        # CurrentTimeF = time.strftime("%Y-%m-%d %H:%M:%S", SampleDate)
        json_body = [{
            "measurement": "twping_snmp",
            "tags": {"src_ip": source_ip, "dst_ip": destination_ip},
            "time": SampleDate,
            "fields": results}]
        write_to_influx(json_body)
        sleep(int(sleep_time))
