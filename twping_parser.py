import re
from influx_client import write_to_influx

src_ip = "10.1.3.100"
dst_ip = "10.1.1.100"

def parse_twping(twping_results_file):
    twping_service={}
    sid = re.compile('SID:\t(?P<sid>.*)')
    first = re.compile('first:\t(?P<first>.*)')
    last = re.compile('last:\t(?P<time>.*)')
    rtt = re.compile('round-trip time min/median/max = (?P<rtt_min>\d{1,10}(\.\d{1,4})?)/(?P<rtt_median>\d{1,10}(\.\d{1,4})?)/(?P<rtt_max>\d{1,10}(\.\d{1,4})?).*')
    send_time = re.compile('send time min/median/max = (?P<send_time_min>\d{1,10}(\.\d{1,4})?)/(?P<send_time_median>\d{1,10}(\.\d{1,4})?)/(?P<send_time_max>\d{1,10}(\.\d{1,4})?).*')
    reflect_time = re.compile('reflect time min/median/max = (?P<reflect_time_min>\d{1,10}(\.\d{1,4})?)/(?P<reflect_time_median>\d{1,10}(\.\d{1,4})?)/(?P<reflect_time_max>\d{1,10}(\.\d{1,4})?).*')
    two_way_jitter = re.compile('two-way jitter = (?P<two_way_jitter>\d{1,10}(\.\d{1,4})?).*')
    send_jitter = re.compile('send jitter = (?P<send_jitter>\d{1,10}(\.\d{1,4})?).*')
    reflect_jitter = re.compile('reflect jitter = (?P<reflect_jitter>\d{1,10}(\.\d{1,4})?).*')

    regex_list=[sid,first,last,rtt,send_time,reflect_time,two_way_jitter,send_jitter,reflect_jitter]
    with open(twping_results_file) as fp:
        line = fp.readline()
        line = line.strip()
        cnt = 1
        while line:
            # print(line)
            for i in regex_list:
                matched_expression = i.match(line)
                if(matched_expression):
                    matched_dict = matched_expression.groupdict()
                    twping_service.update(matched_dict)

            line = line.strip()
            line = fp.readline()
    return twping_service



    # while line:
    #     lin = line.strip()
    #     matched_expression = sid.match(lin)
    #     print(matched_expression)
