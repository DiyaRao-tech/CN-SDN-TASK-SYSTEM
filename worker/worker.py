import socket, json, sys

name = sys.argv[1]
server_ip = sys.argv[2] if len(sys.argv) > 2 else "127.0.0.1"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((server_ip, 5000))
f = s.makefile("rw")

f.write(json.dumps({"type": "REGISTER", "name": name}) + "\n")
f.flush()

task = json.loads(f.readline())
print("Got task", task)

result = task["data"] ** 2
f.write(json.dumps({"type": "RESULT", "id": task["id"], "result": result}) + "\n")
f.flush()
print("Sent result", result)
s.close()
