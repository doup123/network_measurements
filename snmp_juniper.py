#! /usr/bin/env python3.5

from pysnmp.hlapi import *
import time
import sys
from influxdb import InfluxDBClient
from testbed import *
import logging
import threading


def write_to_influx(measurements):
    client = InfluxDBClient(influxdb_ip, infuxdb_port, influxdb_username, influxdb_passwd, influxdb_db)
    client.write_points(measurements)



logging.basicConfig(level=logging.INFO, format=' %(asctime)s - %(levelname)s - %(message)s')

def dateToString(myDate):
    year = str((myDate[0] * 256 + myDate[1])) + '-' + str(myDate[2]) + '-' + str(myDate[3]) +', '
    hour = str(myDate[4]) + ':' + str(myDate[5]) + ':' + str(myDate[6])
    return year + hour


#Gloval varialbles                 


jnxTwampClientResultsSampleEntry = ObjectIdentifier('1.3.6.1.4.1.2636.3.77.1.1.1.1')
jnxTwampResSampleValue = ObjectIdentifier('1.3.6.1.4.1.2636.3.77.1.1.1.1.2')
jnxTwampResSampleDate = ObjectIdentifier('1.3.6.1.4.1.2636.3.77.1.1.1.1.3')


EntryLength = len(jnxTwampClientResultsSampleEntry)

StopPolling = False

#conn = pymysql.connect(host='localhost', port=3306, user='victorolifer', passwd='', db='rpm')

#cur = conn.cursor()

while StopPolling == False:
    
        
    abc = jnxTwampClientResultsSampleEntry
 
      
    logging.info("Start of next poll ")
   
    for i in range(150):
 
        errorIndication, errorStatus, errorIndex, varBinds = next(
            nextCmd(SnmpEngine(),
                CommunityData('public', mpModel=0),
                UdpTransportTarget(('172.16.0.194', 161)),
                ContextData(),
                ObjectType(ObjectIdentity(abc)))
            )


        if errorIndication:
            print(errorIndication)
            break
        elif errorStatus:
            print('%s at %s' % (errorStatus.prettyPrint(),
                            errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
        else:
        
#            logging.info("Start of the nex poll ")
            varBind = varBinds[0]
            abc = varBind[0]
            abcLen = len(abc)
            abcType = abc[abcLen -1]
            abcValueDate = abc[EntryLength]
#            print('abcValueDate= ', abcValueDate)
#            print('abcType= ', abcType)
#            print ('abc= ', abc, 'varBinds[0]= ', varBinds[0])
#            print ('abcLen= ', str(abcLen))

            if abcValueDate == 2:
            
                if abcType == 1:
                    roundTripTime = str(varBind[1])
                    TestName = ''
                    TestNameLength = abcLen - EntryLength - 2 
                    ptr = EntryLength + 1
                    for i in range(ptr, ptr + TestNameLength):
                        TestName = TestName + chr(abc[i])
#                    print('TestName: ' + TestName)
#                    print('abc: ', abc)
#                    print('varBinds', varBinds)
#                    print('varBinds[0]: ', varBinds[0])
                    continue 
            
 
                elif abcType == 2:
                    rttJitter = str(varBind[1])
                    continue
                elif abcType == 3:
                    rttInterarrivalJitter = str(varBind[1])
                    continue
                elif abcType == 4:
                    egress = str(varBind[1])
                    continue
                elif abcType == 5:
                    egressJitter = str(varBind[1])
                    continue
                elif abcType == 6:
                    egressInterarrivalJitter  = str(varBind[1])
                    continue
                elif abcType == 7:
                    ingress = str(varBind[1])
                    continue
                elif abcType == 8:
                    ingressJitter   = str(varBind[1])
                    continue
                elif abcType == 9:
                    ingressInterarrivalJitter = str(varBind[1])
                    continue
            elif abcValueDate == 3:
                SampleDate = dateToString(varBind[1])
                print('abc: ', abc)
                print('SampleDate: ', SampleDate)
                print('roundTripTime: ', roundTripTime)
                print('egress: ', egress)
                print ('ingress: ', ingress)
                print('Going to the nex poll')
                tt = time.time();
                ttt = time.gmtime(tt)
                CurrentTimeF = time.strftime("%Y-%m-%d %H:%M:%S", ttt)
                twping_service = {}
                twping_service["rtt"]=float(roundTripTime)/1000.0
                twping_service["rttJitter"]=float(rttJitter)/1000.0
		
                json_body = [{
	        "measurement": "twping_snmp",
       		"tags": {"src_ip":"10.4.2.1", "dst_ip":"10.4.4.1"},
	        "time": CurrentTimeF,
	        "fields": twping_service
    }]
                write_to_influx(json_body) 
                print('Starting saving results in twamp5 table')
                #sql = "INSERT INTO `twamp5` VALUES (%s, %s, %s, %s, %s)"
                #cur.execute(sql, (CurrentTimeF, int(roundTripTime), int(egress), int(ingress), TestName ))
                #conn.commit()

                time.sleep(10)
                break
        
 
print('End of polling')

                      
                
                       
                
        


     

    



