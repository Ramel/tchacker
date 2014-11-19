#!/bin/bash

#workon 0.62
cd /home/tchack/Dev/venv/0.62/ikaaro-tchack-com-0.62/

/home/tchack/Dev/venv/0.62/bin/icms-stop.py /home/tchack/Dev/venv/0.62/ikaaro-tchack-com-0.62
# service ikaaro_tchack_com-0.62 stop
echo "stopped"

#for KILLPID in `ps ax | grep 'ikaaro-tchack-com-0.62' | awk ' { print $1;}'`; do
#  killal1l -9 $KILLPID;
#  echo "kill -9 ${KILLPID}";
#done

#kill -9 `ps ax | awk 'ikaaro-tchack-com-0.62 { print $1 }'`
pkill -f ikaaro-tchack-com-0.62

rm pid-subprocess

screen -dm /home/tchack/Dev/venv/0.62/bin/icms-start.py /home/tchack/Dev/venv/0.62/ikaaro-tchack-com-0.62

#service ikaaro_tchack_com-0.62 start
echo "re-starting"
