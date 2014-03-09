#!/bin/bash

localhost_server="$1"

ip_addr="`ifconfig eth0 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}'`"

if [ -z "$localhost_server" ]; then
  sudo python manage.py runserver $ip_addr:80
else
  sudo python manage.py runserver
fi
