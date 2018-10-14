#!/bin/bash

function start() {
  if [ "$(lsof -t -i :2020)" ]; then
    echo "RaspberryCast server is already running."
    return
  fi
	echo "Checking for updates."
	git pull
	echo "Starting RaspberryCast server."
	./server.py &
	echo "Done."
}

function stop() {
	echo "Killing RaspberryCast..."
	sudo killall omxplayer.bin >/dev/null 2>&1
	sudo killall python >/dev/null 2>&1
	kill "$(lsof -t -i :2020)" >/dev/null 2>&1
	rm ./*.srt >/dev/null 2>&1
	echo "Done."
}

restart() {
  stop && start
}

function status() {
  echo -n "RaspberryCast is ... "
  [ "$(lsof -t -i :2020)" ] && echo "UP" || echo "DOWN"
}

if [ "$(id -u)" = "0" ]
then
  echo "Please start this script without root privileges!"
  echo "Try again without sudo."
  exit 0
fi

case "$1" in
start)
  start
  ;;
stop)
  stop
  ;;
restart)
  restart
  ;;
status)
  status
  ;;
*)
  echo "Usage: $0 {start|stop|restart|status}"
  ;;
esac
