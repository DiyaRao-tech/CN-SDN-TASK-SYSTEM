import socket, threading, json, time, sys

NUM = int(sys.argv[1]) if len(sys.argv) > 1 else 30
WORKERS = 3
lock = threading.Lock()
idx = [0]
done = [0]
start = [None]
load = {}

def handle(conn):
    f = conn.makefile("rw")
    name = json.loads(f.readline())["name"]
    with lock:
        k = idx[0]
        idx[0] += 1
        if start[0] is None:
            start[0] = time.time()
    n = 0
    for i in range(1, NUM + 1):
        if (i - 1) % WORKERS != k:
            continue
        f.write(json.dumps({"type": "TASK", "id": i, "data": i}) + "\n")
        f.flush()
        json.loads(f.readline())
        n += 1
        with lock:
            done[0] += 1
            load[name] = n
            if done[0] == NUM:
                print("STATIC DONE in %.2f s" % (time.time() - start[0]), load, flush=True)
    f.write(json.dumps({"type": "DONE"}) + "\n")
    f.flush()
    conn.close()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("0.0.0.0", 5000))
s.listen()
print("Static server listening", flush=True)
while True:
    conn, addr = s.accept()
    threading.Thread(target=handle, args=(conn,), daemon=True).start()
