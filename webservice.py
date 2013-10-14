#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
import socket
import threading
 
host = ""
port = 5000
 
class Connect(threading.Thread):
    def __init__(self, sock, addr):
        self.sock = sock
        self.addr = addr
        threading.Thread.__init__(self)
    def run (self):
        while True:
            buf = self.sock.recv(1024)
            if buf == "exit":
                self.sock.send("bye")
                break
            elif buf:
                self.sock.send(buf)
        self.sock.close()
 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((host, port))
s.listen(5)
while True:
    sock, addr = s.accept()
    Connect(sock, addr).start()
