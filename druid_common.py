#vim: set fileencoding=utf-8 
import argparse
import sys
from string import maketrans
from datetime import datetime
import time
from colored import ColoredString
from time import sleep
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
            dest="head", default="50",
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

def format_rows(rows):
    maxlens = [0] * len(rows[0])
    for row in rows:
        for index,field in enumerate(row) :
            if isinstance(field,ColoredString) :
                if (field.len()>maxlens[index]):
                    maxlens[index] = field.len()
            else :
                field = str(field)
                if (len(field)>maxlens[index]):
                    maxlens[index] = len(field)

    headline = ""
    for item in maxlens:
        headline = headline + "+" + ("-"*item) + "--"
    headline = headline+ "+" 

    formated_rows = []
    tail_split = False
    for rowindex,row in enumerate(rows):
        line = ""
        # if row is empty,than make a split line
        if (row == []) :
            formated_rows.append(headline)
            if rowindex == len(rows) - 1 :
                tail_split = True
        else :
            for index,field in enumerate(row):
                if isinstance(field,ColoredString) :
                    line = line+ "| " + field.ljust(maxlens[index] + 1)
                else :
                    field = str(field)
                    line = line+ "| " + field.ljust(maxlens[index] + 1)
            if rowindex == 1 : formated_rows.append(headline)
            formated_rows.append(line + "|")
    if not tail_split :
        formated_rows.append(headline)
    return formated_rows

def print_stat_desc(file_name):
    for line in open(file_name):
        print convert_sys_encode(line.replace("\n",""))
    print ""

def parse_time(value, format_str):
    if value == None or value == "" :
        return ""
    #already formatted in "2013-08-14 09:24:22" format
    if len(value) == 19 :
        return value
    
    if hasattr(datetime, 'strptime'):
        #python 2.6
        strptime = datetime.strptime
    else:
        #python 2.4 equivalent
        strptime = lambda date_string, format: datetime(*(time.strptime(date_string, format)[0:6]))

    return strptime(value,format_str)
    

def print_ds_tabled_stat(color_info, host_info):
    rows = []
    title_row = ["Host","Name","MaxAct","MinIdle","IniSize","PoolCt","ActCt","PoolPk","PoolPkT","ActPk","ActPkT","PhyCc","LogicCc","LCEC","PCEC","PhyClose"]
    rows.append(title_row)
    for host_name in host_info :
        url = host_info[host_name]
        result = fetch_json_result(url,"/druid/datasource.json")
        for data_content in result.get("Content") :
            row = [host_name]
            row.append(data_content.get("Name"))
            row.append(data_content.get("MaxActive"))
            row.append(data_content.get("MinIdle"))
            row.append(data_content.get("InitialSize"))

            row.append(get_colored_value(color_info,data_content.get("PoolingCount"),"PoolingCount"))
            row.append(get_colored_value(color_info,data_content.get("ActiveCount"),"ActiveCount"))
            #row.append(data_content.get("PoolingCount"))
            #row.append(data_content.get("ActiveCount"))

            row.append(data_content.get("PoolingPeak"))

            pkt_datetime = parse_time(data_content.get("PoolingPeakTime"), "%a %b %d %H:%M:%S CST %Y")
            if not isinstance(pkt_datetime,str)   :
                row.append(pkt_datetime.strftime("%m-%d %H:%M:%S"))
            else :
                row.append(pkt_datetime)

            row.append(data_content.get("ActivePeak"))

            apt_datetime = parse_time(data_content.get("ActivePeakTime"), "%a %b %d %H:%M:%S CST %Y")
            if not isinstance(apt_datetime,str)   :
                row.append(apt_datetime.strftime("%m-%d %H:%M:%S"))
            else :
                row.append(apt_datetime)

            row.append(get_colored_value(color_info,data_content.get("PhysicalConnectCount"),"PhysicalConnectCount"))
            row.append(get_colored_value(color_info,data_content.get("LogicConnectCount"),"LogicConnectCount"))
            row.append(get_colored_value(color_info,data_content.get("LogicConnectErrorCount"),"LogicConnectErrorCount"))
            row.append(get_colored_value(color_info,data_content.get("PhysicalConnectErrorCount"),"PhysicalConnectErrorCount"))
            row.append(get_colored_value(color_info,data_content.get("PhysicalCloseCount"),"PhysicalCloseCount"))

            #row.append(data_content.get("PhysicalConnectCount"))
            #row.append(data_content.get("LogicConnectCount"))
            #row.append(data_content.get("LogicConnectErrorCount"))
            #row.append(data_content.get("PhysicalConnectErrorCount"))
            #row.append(data_content.get("PhysicalCloseCount"))
            rows.append(row)


    formated_rows = format_rows(rows)
    title = "  DataSource Stat Result  "
    padstr = "=" * ( (len(formated_rows[0]) - len(title)) / 2 )
    print padstr + title + padstr
    for line in formated_rows :
        print line
    print ""
    print ""


def print_sql_tabled_stat(color_info, host_info, sort_field, head_count):
    rows = []
    title_row = ["Host","ID", "SQL", "ExeCnt","LastTime","Histo","MaxTimeSpan","MOT","ExeHoldHisto","FetchRowCountHistogram"]

    rows.append(title_row)
    for host_name in host_info :
        url = host_info[host_name]
        result = fetch_json_result(url,"/druid/sql.json")
        data_content =  result.get("Content")
        if data_content == None:
            continue
        data_content = filter_sql_result(data_content,sort_field, head_count)
        for item in data_content :
            row = [host_name]
            row.append(item.get("ID"))
            sql = item.get("SQL").replace("\n"," ").strip()[0:30]
            row.append(convert(sql))
            #row.append(item.get("ResultSetHoldTime"))
            row.append(get_colored_value(color_info,item.get("ExecuteCount"),"ExecuteCount"))

            row.append(convert_time(item.get("LastTime")))
            #row.append(item.get("EffectedRowCountHistogram"))
            histogram = get_colored_histo(color_info,item.get("Histogram"),"Histogram")
            row.append(histogram)
            #row.append(item.get("BatchSizeMax"))
            row.append(get_colored_value(color_info,item.get("MaxTimespan"),"MaxTimespan"))
            row.append(convert_time(item.get("MaxTimespanOccurTime")))
            #row.append(item.get("ErrorCount"))

            holdHistor = get_colored_histo(color_info, item.get("ExecuteAndResultHoldTimeHistogram"),"ExecuteAndResultHoldTimeHistogram")
            row.append(holdHistor)
            #row.append(item.get("ConcurrentMax"))
            #row.append(item.get("FetchRowCount"))
            fetchRowHistor = get_colored_histo(color_info,item.get("FetchRowCountHistogram"),"FetchRowCountHistogram")
            row.append(fetchRowHistor)
            #row.append(item.get("InTransactionCount"))
            #row.append(item.get("ID"))
            #row.append(item.get("RunningCount"))
            #row.append(item.get("TotalTime"))
            #row.append(item.get("EffectedRowCount"))
            #row.append(item.get("DbType"))
            rows.append(row)
        rows.append([])

    formated_rows = format_rows(rows)
    title = "  SQL Stat Result  "
    padstr = "=" * ( (len(formated_rows[0]) - len(title)) / 2 )
    print padstr + title + padstr
    for line in formated_rows :
        print line
    print ""
    print ""

def filter_sql_result(data_content, sort_field, head_count):
    
    def cmp_execnt(v1,v2):
        c1 = v1.get("ExecuteCount")
        c2 = v2.get("ExecuteCount")
        return c1 - c2

    def cmp_maxtimespan(v1,v2):
        c1 = v1.get("MaxTimespan")
        c2 = v2.get("MaxTimespan")
        return c1 - c2

    def cmp_histo(v1,v2):
        c1 = v1.get("Histogram")
        c2 = v2.get("Histogram")
        return _cmp_histo(c1,c2)

    def cmp_exeholdhisto(v1,v2):
        c1 = v1.get("ExecuteAndResultHoldTimeHistogram")
        c2 = v2.get("ExecuteAndResultHoldTimeHistogram")
        return _cmp_histo(c1,c2)

    def _cmp_histo(c1,c2):
        result = 0
        for i in range(len(c1)-1,-1,-1):
            if c1[i] == c2[i] :
                continue
            result = c1[i] - c2[i]
            break
        return result


    sort_method = None
    if sort_field == "ExeCnt":
        sort_method = cmp_execnt
    elif sort_field == "Histo":
        sort_method = cmp_histo
    elif sort_field == "MaxTimeSpan":
        sort_method = cmp_maxtimespan
    elif sort_field == "ExeHoldHisto":
        sort_method = cmp_exeholdhisto

    data_content = sorted(data_content,cmp=sort_method, reverse=True)
    data_content = data_content[0:head_count]
    return data_content

def print_activeconn_info(host_info):
    rows = []
    for host_name in host_info :
        url = host_info[host_name]
        result = fetch_json_result(url,"/druid/activeConnectionStackTrace.json")
        content =  result.get("Content")
        if len(content) == 0 :
            print "no active connection at current time."
        for act_info in content :
            for stack_info in act_info :
                lines =  stack_info.split("\n")
                for line in lines :
                    print line
                print "-"*100


if __name__ == "__main__" :
    args_info = parse_args()
    host_info = read_conf(args_info.cfile)

    if args_info.nocolor:
        color_info = {}
    else :
        color_info = read_color_conf()

    if args_info.print_stat_desc :
        print_stat_desc("ds_help.txt")
        print_stat_desc("sql_help.txt")

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

    while True:
        if args_info.show_data == "datasource" or args_info.show_data == None:
            print_ds_tabled_stat(color_info, host_info)
        if args_info.show_data == "sql" or args_info.show_data == None:
            print_sql_tabled_stat(color_info, host_info,args_info.sort_field, int(args_info.head))
        if args_info.show_data == "act" :
            print_activeconn_info(host_info)

        if args_info.interval == None :
            break
        sleep(int(args_info.interval))

        if os.name == "posix" :
            os.system("clear")
        else :
            os.system("cls")

