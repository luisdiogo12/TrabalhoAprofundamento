import sys
import pytest
from subprocess import Popen, PIPE

def server(args):
    for i in iter(Popen(f"python3 {args}", stdout=PIPE, shell=True).stdout.readline, b''):
        return i.decode("utf-8")

def test_ports():
    assert "[ERROR] Invalid port!\n" == server("server.py adda")
    assert "[ERROR] Invalid port!\n" == server("server.py 65d6")
    assert "[ERROR] Invalid port!\n" == server("server.py -3245")
    assert "[ERROR] Invalid port!\n" == server("server.py 0")

def test_agrv():
    assert "[ERROR] Invalid number of arguments!\n" == server("server.py")
    assert "[ERROR] Invalid number of arguments!\n" == server("server.py 12415 adadad")
    assert "[ERROR] Invalid number of arguments!\n" == server("server.py dadad dadad 1314")