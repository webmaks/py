#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import socket
import threading

host = ""
port = 2223

class Connect(threading.Thread):
    def __init__(self, sock, addr):
        self.sock = sock
        self.addr = addr
        threading.Thread.__init__(self)
    def run (self):
        while True:
            buf = self.sock.recv(1024)
            filehandle = open("messages.log", "a")
            print buf
            if buf == "exit":
                self.sock.send("bye")
                break
            elif buf:
                #self.sock.send(buf)
                filehandle.write(buf + "\n")
        self.sock.close()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((host, port))
s.listen(5)
while True:
    sock, addr = s.accept()
    Connect(sock, addr).start()
root@mygps:~# cat workserver.py
#!/usr/bin/env python
import multiprocessing
import socket

def Parser(fullstring):
    "Function for parsing gps messages. For usage: Parser(message)"
    import time
    import MySQLdb
    # Connecting to database
    db = MySQLdb.connect(host="localhost", user="root", passwd="kAysVFVd0Y", db="mygps", charset="utf8")
    cursor = db.cursor()

    # Split message by comma
    fullstring = fullstring
    allparams = fullstring.split(",")

    # If message sent only IMEI or ID or some else wrong message
    try:
        lat = allparams.index("N")
    except:
        lat = ""
    if lat != "":
        # Set variables
        imei = allparams[0][5:]
        lat = str(allparams[allparams.index("N")-1]) #str(float(allparams[allparams.index("N")-1])/100)
        lon = str(allparams[allparams.index("E")-1]) #str(float(allparams[allparams.index("E")-1])/100)
        speed = allparams[allparams.index("E") + 1]
        time = time.time()
        alt = 0
        source = allparams[1]

        # If message hasn't imei
        if not allparams[0].startswith("imei"):
            imei = "GPRMC"

        # Insert into DB
        insert = """insert into gps_data(`lat`,`lon`,`speed`,`time`,`alt`,`imei`,`source`,`data_source`) values(%s,%s,%s,%s,%s,%s,%s,%s)"""
        cursor.execute(insert,(lat,lon,speed,time,alt,imei,source,fullstring))
        db.commit()
        db.close()

def handle(connection, address):
    import logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("process-%r" % (address,))
    try:
        logger.debug("Connected %r at %r", connection, address)
        while True:
            f = open("messages.log", "a")
            data = connection.recv(1024)
            if data == "":
                logger.debug("Socket closed remotely")
                break
            logger.debug("Received data %r", data)
            f.write(data + "\n")
            f.close()
            Parser(data)
            #connection.sendall(data)
            #logger.debug("Sent data")

    except:
        logger.exception("Problem handling request")
    finally:
        logger.debug("Closing socket")
        connection.close()

class Server(object):
    def __init__(self, hostname, port):
        import logging
        self.logger = logging.getLogger("server")
        self.hostname = hostname
        self.port = port

    def start(self):
        self.logger.debug("listening")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.hostname, self.port))
        self.socket.listen(1)

        while True:
            conn, address = self.socket.accept()
            self.logger.debug("Got connection")
            process = multiprocessing.Process(target=handle, args=(conn, address))
            process.daemon = True
            process.start()
            self.logger.debug("Started process %r", process)

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    server = Server("0.0.0.0", 2223)
    try:
        logging.info("Listening")
        server.start()
    except:
        logging.exception("Unexpected exception")
    finally:
        logging.info("Shutting down")
        for process in multiprocessing.active_children():
            logging.info("Shutting down process %r", process)
            process.terminate()
            process.join()
    logging.info("All done")
