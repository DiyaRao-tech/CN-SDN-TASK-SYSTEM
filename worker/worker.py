import socket, json, sys, time

name = sys.argv[1]
server_ip = sys.argv[2]
delay = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5

s = socket.create_connection((server_ip, 5000))
f = s.makefile("rw")
f.write(json.dumps({"type": "REGISTER", "name": name}) + "\n")
f.flush()
while True:
    line = f.readline()
    if not line:
        break
    msg = json.loads(line)
    if msg["type"] == "DONE":
        break
    time.sleep(delay)
    result = msg["data"] ** 2
    f.write(json.dumps({"type": "RESULT", "id": msg["id"], "result": result}) + "\n")
    f.flush()
    print("Task", msg["id"], "->", result, flush=True)
s.close()
