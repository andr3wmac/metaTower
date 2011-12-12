#!/bin/bash
# /etc/init.d/metaTower
# version 0.3.6 2011-10-17 (YYYY-MM-DD)

### BEGIN INIT INFO
# Provides:   metaTower
# Required-Start: $local_fs $remote_fs
# Required-Stop:  $local_fs $remote_fs
# Should-Start:   $network
# Should-Stop:    $network
# Default-Start:  2 3 4 5
# Default-Stop:   0 1 6
# Short-Description:    metaTower Server
# Description:    Starts the metaTower server
### END INIT INFO

#Settings
SERVICE='metaTower.py'
PATH='/home/andrew/dev/metaTower/'

mt_start() {
    if /usr/bin/pgrep -u $USER -f $SERVICE > /dev/null
    then
        echo "metaTower is already running!"
    else
        echo "Starting metaTower..."
        cd $PATH
        /usr/bin/screen -dmS metaTower /usr/bin/python $SERVICE
        /bin/sleep 3
        if /usr/bin/pgrep -u $USER -f $SERVICE > /dev/null
        then
            echo "metaTower is now running."
        else
            echo "Error! Could not start metaTower"
        fi
    fi
}

mt_stop() {
    if /usr/bin/pgrep -u $USER -f $SERVICE > /dev/null
    then
        echo "Stopping metaTower..."
        /usr/bin/screen -p 0 -S metaTower -X quit
        /bin/sleep 3
    else
        echo "metaTower was not running."
    fi
    if /usr/bin/pgrep -u $USER -f $SERVICE > /dev/null
    then
        echo "Error! metaTower could not be stopped."
    else
        echo "metaTower is stopped."
    fi
}

#Start-Stop here
case "$1" in
    start)
        mt_start
        ;;
    stop)
        mt_stop
        ;;
    restart)
        mt_stop
        mt_start
        ;;
    *)

    echo "Usage: /etc/init.d/metaTower {start|stop|restart}"
    exit 1
    ;;
esac

exit 0
