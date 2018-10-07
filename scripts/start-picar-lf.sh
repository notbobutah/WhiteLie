#!/bin/bash

# Redirect standard out and standard error to a file.
exec &> /var/log/picar-service.log
echo $(date +"%D %T")" Begin."

(
    sleep 30
    echo $(date +"%D %T")" 30s elapsed, starting picar."
    sudo python /home/pi/Whiteline/example/line_follower.py &
) &

exit 0
