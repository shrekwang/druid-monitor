#vim: set fileencoding=utf-8 
import urllib2
import simplejson
import pprint
import argparse
import sys
from string import maketrans
from datetime import datetime
import time
from colored import ColoredString


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

def convert_time(value):
    d1 = datetime.fromtimestamp(value/1000.0)
    return d1.strftime("%m-%d %H:%M:%S")

def fetch_json_result(host,query_path):
    url = host + query_path
    req = urllib2.Request(url, None, {'user-agent':'python'})
    opener = urllib2.build_opener()
    f = opener.open(req)
    result = simplejson.load(f,strict=False)
    return result

def parse_args():
    parser = argparse.ArgumentParser(description='druid monitor utility ')
    parser.add_argument('--cfile', action="store", 
            dest="cfile", default="druid.conf",
            help='IP地址配置文件,默认值为druid.conf'
            )

    parser.add_argument('--show', action="store", 
            dest="show_data", 
            help='要显示的数据,可以为datasource或sql, 不设置的话显示全部')

    parser.add_argument('--sort', action="store", 
            dest="sort_field", default="Histo",
            help='SQL统计中表格的排序字段,可以是ExeCnt,Histo,MaxTimeSpan,ExeHoldHisto,默认为Histo'
            )

    parser.add_argument('--head', action="store", 
            dest="head", default="50",
            help='SQL统计中显示的记录数, 默认50条'
            )

    parser.add_argument('--print-stat-desc', action="store_true", 
            dest="print_stat_desc",
            help='是否打印datasource统计表格的字段说明'
            )

    return parser.parse_args()

def read_conf(cfg_path):
    lines = open(cfg_path,"r").readlines()
    cfg_dict = {}
    for line in lines:
        if not line.strip() : continue
        if line[0] == "#" : continue
        split_index= line.find (" ")
        if split_index < 0 : continue 
        key = line[0:split_index].strip()
        value = line[split_index+1:].strip()
        cfg_dict[key] = value
    return cfg_dict

def read_color_conf():
    file = open("color.conf","r")
    confs = {}
    for line in file:
        if line.strip() == "" : continue
        if line.strip().startswith("#") : continue
        split_index= line.find ("=")
        if split_index < 0 : continue 
        key = line[0:split_index].strip()
        value = line[split_index+1:].strip()
        try :
            value = eval(value)
            confs[key] = value
        except :
            pass
    return confs


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
        print line.replace("\n","")
    print ""

def parse_time(value, format_str):
    if hasattr(datetime, 'strptime'):
        #python 2.6
        strptime = datetime.strptime
    else:
        #python 2.4 equivalent
        strptime = lambda date_string, format: datetime(*(time.strptime(date_string, format)[0:6]))

    return strptime(value,format_str)
    

def print_ds_tabled_stat(host_info):
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

            row.append(get_colored_value(data_content.get("PoolingCount"),"PoolingCount"))
            row.append(get_colored_value(data_content.get("ActiveCount"),"ActiveCount"))
            #row.append(data_content.get("PoolingCount"))
            #row.append(data_content.get("ActiveCount"))

            row.append(data_content.get("PoolingPeak"))

            pkt_datetime = parse_time(data_content.get("PoolingPeakTime"), "%a %b %d %H:%M:%S CST %Y")
            row.append(pkt_datetime.strftime("%m-%d %H:%M:%S"))

            row.append(data_content.get("ActivePeak"))

            apt_datetime = parse_time(data_content.get("ActivePeakTime"), "%a %b %d %H:%M:%S CST %Y")
            row.append(apt_datetime.strftime("%m-%d %H:%M:%S"))

            row.append(get_colored_value(data_content.get("PhysicalConnectCount"),"PhysicalConnectCount"))
            row.append(get_colored_value(data_content.get("LogicConnectCount"),"LogicConnectCount"))
            row.append(get_colored_value(data_content.get("LogicConnectErrorCount"),"LogicConnectErrorCount"))
            row.append(get_colored_value(data_content.get("PhysicalConnectErrorCount"),"PhysicalConnectErrorCount"))
            row.append(get_colored_value(data_content.get("PhysicalCloseCount"),"PhysicalCloseCount"))

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

def get_colored_histo(value,name):
    str_value = ",".join([str(v) for v in value])
    color_conf = color_info.get(name)
    if color_conf == None :
        return str_value
    sorted_conf = sorted(color_conf.iteritems(),reverse=True)
    matched_color = None
    for i in range(len(value)-1,-1,-1):
        for limit,color in  sorted_conf :
            if i >= limit and value[i] > 0 :
                matched_color = color
                break
        if matched_color != None :
            break
    if matched_color == None :
        return str_value
    return ColoredString(str_value,color)

def get_colored_value(value,name):
    color_conf = color_info.get(name)
    if color_conf == None :
        return value
    sorted_conf = sorted(color_conf.iteritems(),reverse=True)
    matched_color = None
    for limit,color in  sorted_conf :
        if value >= limit : 
            matched_color = color
            break
    if matched_color == None :
        return value
    return ColoredString(value,color)


def print_sql_tabled_stat(host_info, sort_field, head_count):
    rows = []
    title_row = ["Host", "SQL", "ExeCnt","LastTime","Histo","MaxTimeSpan","MOT","ExeHoldHisto","FetchRowCountHistogram"]

    rows.append(title_row)
    for host_name in host_info :
        url = host_info[host_name]
        result = fetch_json_result(url,"/druid/sql.json")
        data_content =  result.get("Content")
        data_content = filter_sql_result(data_content,sort_field, head_count)
        for item in data_content :
            row = [host_name]
            sql = item.get("SQL").replace("\n"," ").strip()[0:30]
            row.append(convert(sql))
            #row.append(item.get("ResultSetHoldTime"))
            row.append(get_colored_value(item.get("ExecuteCount"),"ExecuteCount"))

            row.append(convert_time(item.get("LastTime")))
            #row.append(item.get("EffectedRowCountHistogram"))
            histogram = get_colored_histo(item.get("Histogram"),"Histogram")
            row.append(histogram)
            #row.append(item.get("BatchSizeMax"))
            row.append(get_colored_value(item.get("MaxTimespan"),"MaxTimespan"))
            row.append(convert_time(item.get("MaxTimespanOccurTime")))
            #row.append(item.get("ErrorCount"))

            holdHistor = get_colored_histo(item.get("ExecuteAndResultHoldTimeHistogram"),"ExecuteAndResultHoldTimeHistogram")
            row.append(holdHistor)
            #row.append(item.get("ConcurrentMax"))
            #row.append(item.get("FetchRowCount"))
            fetchRowHistor = get_colored_histo(item.get("FetchRowCountHistogram"),"FetchRowCountHistogram")
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


if __name__ == "__main__" :
    args_info = parse_args()
    host_info = read_conf(args_info.cfile)
    global color_info
    color_info = read_color_conf()
    if args_info.print_stat_desc :
        print_stat_desc("ds_help.txt")
        print_stat_desc("sql_help.txt")

    if args_info.show_data == "datasource" or args_info.show_data == None:
        print_ds_tabled_stat(host_info)
    if args_info.show_data == "sql" or args_info.show_data == None:
        print_sql_tabled_stat(host_info,args_info.sort_field, int(args_info.head))

