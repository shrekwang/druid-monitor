druid-monitor
=============

druid-monitor is a command-line tool for collecting and displaying druid statistic data from various hosts.

Requirments
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

python druid_common.py -h --cfile filename --show dataname
      --sort sortfield --head headcount --print-stat-desc

请先用 "python druid_common.py -h"　调用下,看看各个参数的描述.


