#!/usr/bin/env python3

from subprocess import Popen, PIPE
from json import loads, dumps
from datetime import date
import socket
import os
import psycopg2
from psycopg2 import sql

def get_statistics():
  statisticslist = []
  hostname = socket.gethostname()
  vnstat = Popen(["vnstat", "--json"], stdout=PIPE)
  vnstat.wait()
  traffic = loads(vnstat.stdout.read())
  for interface in traffic['interfaces']:
    daily_traffic = interface['traffic']['day']
    for traffic_of_day in daily_traffic:
      dateobj = date(
          traffic_of_day["date"]["year"],
          traffic_of_day["date"]["month"],
          traffic_of_day["date"]["day"]
        )
      rx = traffic_of_day["rx"]
      tx = traffic_of_day["tx"]
      statisticslist.append( {
        "rx" : rx,
        "tx" : tx,
        "date" : dateobj,
        "if": interface['name'],
        "host" : hostname
      } )
  return statisticslist

def get_configuration():
  configuration = None
  homedir = os.getenv("HOME")
  if os.path.isdir(homedir):
    conffile = str.join("/", [homedir, ".vnstatdbimport.conf"])
    if os.path.isfile(conffile):
      conf = open(conffile, "r")
      configuration = loads(conf.read())
      conf.close()
    elif not os.path.exists(conffile):
      conf = open(conffile, "w")
      configuration = {}
      configuration["dbname"] = input("What is your database name? ")
      configuration["user"] = input("What is your user name? ")
      configuration["table"] = input("What is your table name? ")
      conf.write(dumps(configuration, indent=2))
      conf.close()
    else:
      print("something gone wrong, skipping")
  return configuration

if __name__ == "__main__":
  statisticslist = get_statistics()
  configuration = get_configuration()
  dbconn = psycopg2.connect(
    dbname=configuration["dbname"],
    user=configuration["user"]
  )
  dbconn.set_session(autocommit=True)
  cur = dbconn.cursor()
  select_statement = sql.SQL("SELECT * FROM {}").format(sql.Identifier(configuration["table"]))
  insert_statement = sql.SQL("""INSERT INTO {}
    ( host, interface, day, tx, rx )
    VALUES ( %s, %s, %s, %s, %s )""").format(sql.Identifier(configuration["table"]))
  cur.execute(select_statement, (None,None))
  print(cur.fetchall())
  cur.close()
  dbconn.close()
