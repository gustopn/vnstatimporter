#!/usr/bin/env python3

from subprocess import Popen, PIPE
from json import dumps, loads

if __name__ == "__main__":
  vnstat = Popen(["vnstat", "--json"], stdout=PIPE)
  vnstat.wait()
  traffic = loads(vnstat.stdout.read())
  statisticslist = []
  for interface in traffic['interfaces']:
    interfacedict = {
      "name": interface['name'],
      "traffic": []
    }
    daily_traffic = interface['traffic']['day']
    for traffic_of_day in daily_traffic:
      date  = str(traffic_of_day["date"]["year"]) + "-"
      date += str(traffic_of_day["date"]["month"]) + "-"
      date += str(traffic_of_day["date"]["day"])
      rx = traffic_of_day["rx"]
      tx = traffic_of_day["tx"]
      traffic_dict = {
        "rx" : rx,
        "tx" : tx,
        "date" : date
      }
      interfacedict["traffic"].append(traffic_dict)
    statisticslist.append( interfacedict )
  print(dumps(statisticslist, indent=2))

