import sys
import pytest
from subprocess import Popen, PIPE

def client(args):
    for i in iter(Popen(f"python3 {args}", stdout=PIPE, shell=True).stdout.readline, b''):
        return i.decode("utf-8")

def test_ports():
    
    assert "Usage: port must be a number greater than zero\n" == client("client.py Afonso -3343")
    assert "Usage: port must be a number greater than zero\n" == client("client.py Luis 0")

def test_agrv():
    assert "Usage: python3 client.py <id> <port> [machine]\n" == client("client.py adda")
    assert "Usage: python3 client.py <id> <port> [machine]\n" == client("client.py 65d6")
    assert "Usage: python3 client.py <id> <port> [machine]\n" == client("client.py")
    assert "Usage: python3 client.py <id> <port> [machine]\n" == client("client.py Albertino")
    assert "Usage: python3 client.py <id> <port> [machine]\n" == client("client.py Jonas 1245 frafa siiiui edede")
    assert "Usage: python3 client.py <id> <port> [machine]\n" == client("client.py Jonas 1245 9875 ihbvrjk 5757.1.4.5.6")