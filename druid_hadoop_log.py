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


codepage = sys.getdefaultencoding()
#translate control characters
intab = "\x00\x01\x0d\x0a\x09"
outtab = "01   "
trantab = maketrans(intab, outtab)

def convert(value):
    if isinstance(value,unicode) :
        value = value.encode(codepage)
    value = str(value).rstrip().translate(trantab)
    return value

def parse_args():
    parser = argparse.ArgumentParser(description='druid monitor utility ')
    parser.add_argument('-c','--cfile', action="store", 
            dest="cfile", default="druid.conf",
            help=convert_sys_encode('IP地址配置文件,默认值为druid.conf')
            )

    parser.add_argument('-s','--show', action="store", 
            dest="show_data", 
            help=convert_sys_encode('要显示的数据,可以为ds或sql或act, 不设置的话显示ds+sql, act为活动连接堆栈信息'))

    parser.add_argument('-t','--sort', action="store", 
            dest="sort_field", default="Histo",
            help=convert_sys_encode('SQL统计中表格的排序字段,可以是ExeCnt,Histo,MaxTimeSpan,ExeHoldHisto,默认为Histo')
            )

    parser.add_argument('-n', '--num', action="store", 
            dest="head", default="50000",
            help=convert_sys_encode('SQL统计中显示的记录数, 默认50条')
            )

    parser.add_argument('-v','--print-stat-desc', action="store_true", 
            dest="print_stat_desc",
            help=convert_sys_encode('是否打印datasource统计表格的字段说明')
            )

    parser.add_argument('-N', '--nocolor', action="store_true", 
            dest="nocolor",
            help=convert_sys_encode('不按颜色打印(默认是有颜色的)')
            )

    parser.add_argument('-i','--interval', action="store", 
            dest="interval",
            help=convert_sys_encode('自动刷新时间间隔,以秒为单位. 如不指定,则打印后即退出脚本')
            )

    parser.add_argument('-r','--reset', action="store_true", 
            dest="resetAll",
            help=convert_sys_encode('重置所有已配置的主机的统计数据(不能和其他选项合用)')
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
    

def print_ds_tabled_stat(conf_name, color_info, host_info, stat_time):
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
                row.append(pkt_datetime.strftime("%m-%d %H:%M:%S"))
            else :
                row.append("")

            row.append(data_content.get("ActivePeak"))
            apt_datetime = parse_time(data_content.get("ActivePeakTime"), "%a %b %d %H:%M:%S CST %Y")
            if apt_datetime !="" :
                row.append(apt_datetime.strftime("%m-%d %H:%M:%S"))
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

    wfile = open(conf_name + "_DataSource.log","w")
    for line in formated_rows :
        wfile.write(line)
        wfile.write("\n")
    wfile.close()


def print_sql_tabled_stat(conf_name,color_info, host_info, stat_time):
    rows = []

    for host_name in host_info :
        url = host_info[host_name]
        result = fetch_json_result(url,"/druid/sql.json")
        data_content =  result.get("Content")
        for item in data_content :
            row = [stat_time]
            row.append(host_name)
            row.append(item.get("ID"))
            sql = item.get("SQL").replace("\n"," ").strip()[0:30]
            row.append(convert(sql))
            #row.append(item.get("ResultSetHoldTime"))
            row.append(item.get("ExecuteCount"))

            row.append(convert_time(item.get("LastTime")))
            #row.append(item.get("EffectedRowCountHistogram"))
            row.append(item.get("Histogram"))
            #row.append(item.get("BatchSizeMax"))
            row.append(item.get("MaxTimespan"))
            row.append(convert_time(item.get("MaxTimespanOccurTime")))
            #row.append(item.get("ErrorCount"))

            holdHistor = item.get("ExecuteAndResultHoldTimeHistogram")
            row.append(holdHistor)
            #row.append(item.get("ConcurrentMax"))
            #row.append(item.get("FetchRowCount"))
            fetchRowHistor = item.get("FetchRowCountHistogram")
            row.append(fetchRowHistor)
            #row.append(item.get("InTransactionCount"))
            #row.append(item.get("ID"))
            #row.append(item.get("RunningCount"))
            #row.append(item.get("TotalTime"))
            #row.append(item.get("EffectedRowCount"))
            #row.append(item.get("DbType"))
            rows.append(row)
        rows.append([])

    formated_rows = ["#".join([str(ele) for ele in row]) for row in rows]
   
    wfile = open(conf_name + "_SQL.log","w")
    for line in formated_rows :
        wfile.write(line)
        wfile.write("\n")
    wfile.close()
 


if __name__ == "__main__" :
    args_info = parse_args()
    host_info = read_conf(args_info.cfile)
    color_info = {}
    
    if args_info.resetAll:
        for host_name in host_info :
            url = host_info[host_name]
            result = fetch_json_result(url,"/druid/reset-all.json")
            result_code =  result.get("ResultCode")
            if result_code == 1 :
                print "reset " + host_name +" stat data successed."
            else :
                print "fail to reset "+ host_name + " stat data ."
        sys.exit()
    conf_name = args_info.cfile
    if conf_name != "" and ( conf_name.startswith("druid_") or conf_name.startswith("druid-")):
        conf_name,_ = os.path.splitext(conf_name)
        conf_name = conf_name[6:]

    stat_time = strftime("%Y-%m-%d %H:%M:%S", localtime())
    if args_info.show_data == "datasource" or args_info.show_data == None:
        print_ds_tabled_stat(conf_name,color_info, host_info, stat_time)

    print ""

    if args_info.show_data == "sql" or args_info.show_data == None:
        print_sql_tabled_stat(conf_name,color_info, host_info, stat_time)
    


