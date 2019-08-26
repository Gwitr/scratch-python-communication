import os
import time
import socket
import subprocess
import scratch.base

_serv = None

def _run_serv():
    global _serv
    path = os.path.dirname(__file__)
    _serv = subprocess.Popen(["node.exe", path+"\\"+"main.js"], stderr=subprocess.PIPE)
    print(_serv.stderr.readline())  # Will block until the server says it won't
    time.sleep(1)

def CloudConnection():
    try:
        s = socket.create_connection(("localhost", 8080), timeout=2)
    except socket.timeout:
        print("Running server...")
        _run_serv()
    s = socket.create_connection(("localhost", 8080))
    return base.CloudConnection(s)

