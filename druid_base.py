#vim: set fileencoding=utf-8

import urllib2
import simplejson
from datetime import datetime
import time
from colored import ColoredString

def get_colored_value(color_info, value,name):
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

def get_colored_histo(color_info, value,name):
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

def fetch_json_result(host,query_path):
    url = host + query_path
    req = urllib2.Request(url, None, {'user-agent':'python'})
    opener = urllib2.build_opener()
    f = opener.open(req)
    result = simplejson.load(f,strict=False)
    return result

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

def convert_time(value):
    if value == None or value == "" :
        return ""
    try :
        d1 = datetime.fromtimestamp(value/1000.0)
        return d1.strftime("%m-%d %H:%M:%S")
    except :
        return value

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


