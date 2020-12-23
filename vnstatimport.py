#!/usr/bin/env python3

from subprocess import Popen, PIPE
from json import dumps, loads
import socket

if __name__ == "__main__":
  hostname = socket.gethostname()
  vnstat = Popen(["vnstat", "--json"], stdout=PIPE)
  vnstat.wait()
  traffic = loads(vnstat.stdout.read())
  statisticslist = []
  for interface in traffic['interfaces']:
    daily_traffic = interface['traffic']['day']
    for traffic_of_day in daily_traffic:
      date  = str(traffic_of_day["date"]["year"]) + "-"
      date += str(traffic_of_day["date"]["month"]) + "-"
      date += str(traffic_of_day["date"]["day"])
      rx = traffic_of_day["rx"]
      tx = traffic_of_day["tx"]
      statisticslist.append( {
        "rx" : rx,
        "tx" : tx,
        "date" : date,
        "if": interface['name'],
        "host" : hostname
      } )
  print(dumps(statisticslist, indent=2))

