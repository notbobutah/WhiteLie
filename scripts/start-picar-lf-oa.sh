#!/bin/bash

# Redirect standard out and standard error to a file.
sudo exec &> /var/log/picar-service.log
sudo echo $(date +"%D %T")" Begin."

(
    sleep 30
    sudo echo $(date +"%D %T")" 30s elapsed, starting picar."
    sudo python /home/pi/Whiteline/example/line_with_obsavoidance.py &
) &

exit 0

