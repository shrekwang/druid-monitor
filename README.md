druid-monitor
=============

druid-monitor is a command-line tool for collecting and displaying druid statistic data from various hosts.

需求
=============

监控脚本需要python的simplejson模块
如果是redhat系的(rhel, fedora, centos等),可以用yum来安装
yum install python-simplejson

另外监控脚本使用的是druid开放的json API, 所以你还需要在web.xml中作如下配置

    <servlet>
        <servlet-name>DruidStatView</servlet-name>
        <servlet-class>com.alibaba.druid.support.http.StatViewServlet</servlet-class>
    </servlet>
    <servlet-mapping>
      <servlet-name>DruidStatView</servlet-name>
      <url-pattern>/druid/*</url-pattern>
    </servlet-mapping>
  




使用
=============

    命令1: 打印datasource和sql统计

    python druid_common.py [-h] [-c CFILE] [-s SHOW_DATA] [-t SORT_FIELD]
                           [-n HEAD] [-v] [-N] [-i INTERVAL]

    optional arguments:
      -h, --help            show this help message and exit
      -c CFILE, --cfile CFILE
                            IP地址配置文件,默认值为druid.conf
      -s SHOW_DATA, --show SHOW_DATA
                            要显示的数据,可以为datasource或sql, 不设置的话显示全部
      -t SORT_FIELD, --sort SORT_FIELD
                            SQL统计中表格的排序字段,可以是ExeCnt,Histo,MaxTimeSpan
                            ,ExeHoldHisto,默认为Histo
      -n HEAD, --num HEAD   SQL统计中显示的记录数, 默认50条
      -v, --print-stat-desc
                            是否打印datasource统计表格的字段说明
      -N, --nocolor         不按颜色打印(默认是有颜色的)
      -i INTERVAL, --interval INTERVAL
                            自动刷新时间间隔,以秒为单位.
                            如不指定,则打印后即退出脚本

    命令2: 打印单条SQL的细节信息
    python druid_sql.py [-h] [-c CFILE] [-n SQL_ID] [--host HOST]

    optional arguments:
      -h, --help            show this help message and exit
      -c CFILE, --cfile CFILE
                            IP地址配置文件,默认值为druid.conf
      -n SQL_ID, --id SQL_ID
                            要打印详细信息的sql的id
      --host HOST           主机名, 要跟cfile里的配置一致,根据主机名查找url
    
配置
=============

    总共有两个配置文件 druid.conf和color.conf
    druid.conf用来配置要监控的主机,每行两个字段　机器名和url, 以空格分隔,可以用"#"来注释
    color.conf用来配置监控输出的颜色, 在这个文件里有较详细的说明,有需要定制的可以查看这个文件.

截图
=============
![jie tu](http://pic.yupoo.com/shreknull/Cbbz3duC/medish.jpg)

