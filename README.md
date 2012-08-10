druid-monitor
=============

druid-monitor is a command-line tool for collecting and displaying druid statistic data from various hosts.

Requirments
=============

in order to run this utility, you need to insall  python simplejson module.
in centos or rhel , you can install it like this :
yum install python-simplejson

Usage
=============

python druid_common.py -h --cfile filename --show dataname
      --sort sortfield --head headcount --print-stat-desc

please run "python druid_common.py -h" first for a description of all the arguments.


