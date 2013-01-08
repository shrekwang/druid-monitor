#vim: set fileencoding=utf-8 
import argparse
import sys
from string import maketrans
from datetime import datetime
import time
from colored import ColoredString
from time import localtime, strftime
import os
from druid_base import *
import re
import hashlib


codepage = sys.getdefaultencoding()
#translate control characters
intab = "\x00\x01\x0d\x0a\x09"
outtab = "01   "
trantab = maketrans(intab, outtab)

def convert_time2(value):
    if value == None or value == "" :
        return ""
    try :
        d1 = datetime.fromtimestamp(value/1000.0)
        return d1.strftime("%Y-%m-%d %H:%M:%S")
    except :
        return value

def convert(value):
    if isinstance(value,unicode) :
        value = value.encode(codepage)
    value = str(value).rstrip().translate(trantab)
    return value

def parse_args():
    parser = argparse.ArgumentParser(description='druid stat print utility')
    parser.add_argument('-c','--cfile', action="store", 
            dest="cfile", default="druid.conf",
            help=convert_sys_encode('IP地址配置文件,默认值为druid.conf')
            )

    parser.add_argument('-d','--logdir', action="store", 
            dest="logdir", default=".",
            help=convert_sys_encode('打印日志的目录')
            )

    return parser.parse_args()


def parse_time(value, format_str):
    if value == None or value == "" :
        return ""

    if hasattr(datetime, 'strptime'):
        #python 2.6
        strptime = datetime.strptime
    else:
        #python 2.4 equivalent
        strptime = lambda date_string, format: datetime(*(time.strptime(date_string, format)[0:6]))

    return strptime(value,format_str)
    

def log_ds_tabled_stat(conf_name, logdir, host_info, stat_time):
    rows = []
    for host_name in host_info :
        url = host_info[host_name]
        result = fetch_json_result(url,"/druid/datasource.json")
        for data_content in result.get("Content") :
            row = [stat_time]
            row.append(conf_name)
            row.append(host_name)
            row.append(data_content.get("Name"))
            row.append(data_content.get("MaxActive"))
            row.append(data_content.get("MinIdle"))
            row.append(data_content.get("InitialSize"))
            row.append(data_content.get("PoolingCount"))
            row.append(data_content.get("ActiveCount"))
            #row.append(data_content.get("PoolingCount"))
            #row.append(data_content.get("ActiveCount"))
            row.append(data_content.get("PoolingPeak"))

            pkt_datetime = parse_time(data_content.get("PoolingPeakTime"), "%a %b %d %H:%M:%S CST %Y")
            if pkt_datetime != "" :
                row.append(pkt_datetime.strftime("%Y-%m-%d %H:%M:%S"))
            else :
                row.append("")

            row.append(data_content.get("ActivePeak"))
            apt_datetime = parse_time(data_content.get("ActivePeakTime"), "%a %b %d %H:%M:%S CST %Y")
            if apt_datetime !="" :
                row.append(apt_datetime.strftime("%Y-%m-%d %H:%M:%S"))
            else :
                row.append("")

            row.append(data_content.get("PhysicalConnectCount"))
            row.append(data_content.get("LogicConnectCount"))
            row.append(data_content.get("LogicConnectErrorCount"))
            row.append(data_content.get("PhysicalConnectErrorCount"))
            row.append(data_content.get("PhysicalCloseCount"))

            #row.append(data_content.get("PhysicalConnectCount"))
            #row.append(data_content.get("LogicConnectCount"))
            #row.append(data_content.get("LogicConnectErrorCount"))
            #row.append(data_content.get("PhysicalConnectErrorCount"))
            #row.append(data_content.get("PhysicalCloseCount"))
            rows.append(row)


    formated_rows = ["#".join([str(ele) for ele in row]) for row in rows]

    wfile = open(os.path.join(logdir , "DataSource.log"),"a")
    for line in formated_rows :
        wfile.write(line)
        wfile.write("\n")
    wfile.close()


def log_sql_tabled_stat(conf_name, logdir, host_info, stat_time):
    rows = []

    for host_name in host_info :
        url = host_info[host_name]
        result = fetch_json_result(url,"/druid/sql.json")
        data_content =  result.get("Content")
        if data_content == None:
            continue
        for item in data_content :
            row = [stat_time]
            row.append(conf_name)
            row.append(host_name)
            row.append(item.get("ID"))
            sql = item.get("SQL").replace("\n"," ").strip()[0:30]
            row.append(convert(sql))
            #row.append(item.get("ResultSetHoldTime"))
            row.append(item.get("ExecuteCount"))

            #row.append(item.get("EffectedRowCountHistogram"))
            row.append(str(item.get("Histogram"))[1:-1].replace(" ",""))
            row.append(convert_time2(item.get("LastTime")))
            #row.append(item.get("BatchSizeMax"))
            row.append(convert_time2(item.get("MaxTimespanOccurTime")))
            row.append(item.get("MaxTimespan"))
            #row.append(item.get("ErrorCount"))
            row.append(item.get("TotalTime"))

            holdHistor = str(item.get("ExecuteAndResultHoldTimeHistogram"))[1:-1].replace(" ","")
            row.append(holdHistor)
            #row.append(item.get("ConcurrentMax"))
            #row.append(item.get("FetchRowCount"))
            fetchRowHistor = str(item.get("FetchRowCountHistogram"))[1:-1].replace(" ","")
            row.append(fetchRowHistor)

            row.append(hashlib.md5(item.get("SQL")).hexdigest())
            #row.append(item.get("InTransactionCount"))
            #row.append(item.get("ID"))
            #row.append(item.get("RunningCount"))
            #row.append(item.get("EffectedRowCount"))
            #row.append(item.get("DbType"))
            rows.append(row)

    formated_rows = ["#".join([str(ele) for ele in row]) for row in rows]
   
    wfile = open(os.path.join(logdir , "SQL.log"),"a")
    for line in formated_rows :
        wfile.write(line)
        wfile.write("\n")
    wfile.close()
 


if __name__ == "__main__" :
    args_info = parse_args()
    host_info = read_conf(args_info.cfile)
    
    stat_time = strftime("%Y-%m-%d %H:%M:%S", localtime())
    conf_name = args_info.cfile
    pat = re.compile("druid_(?P<name>.*).conf")
    if conf_name != "" :
        match = pat.search(conf_name)
        if match != None :
            conf_name = match.group("name")

    if conf_name == "":
        conf_name = "default"

    log_ds_tabled_stat(conf_name, args_info.logdir, host_info, stat_time)
    log_sql_tabled_stat(conf_name,args_info.logdir, host_info, stat_time)
    


