from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import IPAddr
import threading, socket

log = core.getLogger()
LISTEN_PORT = 9999

def make_match_msg(ip, command):
    msg = of.ofp_flow_mod(command=command)
    msg.priority = 40000
    msg.match.dl_type = 0x0800
    msg.match.nw_dst = IPAddr(ip)
    return msg

def block(ip):
    msg = make_match_msg(ip, of.OFPFC_ADD)
    for con in core.openflow.connections:
        con.send(msg)
    log.info("BLOCK installed for %s", ip)

def unblock(ip):
    msg = make_match_msg(ip, of.OFPFC_DELETE_STRICT)
    for con in core.openflow.connections:
        con.send(msg)
    log.info("BLOCK removed for %s", ip)

def listener():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", LISTEN_PORT))
    s.listen(5)
    log.info("Listening for server events on port %d", LISTEN_PORT)
    while True:
        conn, addr = s.accept()
        data = conn.recv(1024).decode().strip()
        log.info("Event from %s: %s", addr[0], data)
        parts = data.split()
        if len(parts) == 2 and parts[0] == "WORKER_DOWN":
            core.callLater(block, parts[1])
        elif len(parts) == 2 and parts[0] == "WORKER_UP":
            core.callLater(unblock, parts[1])
        conn.sendall(b"OK\n")
        conn.close()

def launch():
    threading.Thread(target=listener, daemon=True).start()
