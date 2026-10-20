import socket, threading, json

HOST = "0.0.0.0"
PORT = 5000

def handle_worker(conn, addr):
    f = conn.makefile("rw")
    msg = json.loads(f.readline())
    if msg["type"] == "REGISTER":
        name = msg["name"]
        print("Registered", name, "from", addr)
        task = {"type": "TASK", "id": 1, "data": 12}
        f.write(json.dumps(task) + "\n")
        f.flush()
        reply = json.loads(f.readline())
        print("Result from", name, ":", reply)
    conn.close()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen()
print("Server listening on port", PORT)
while True:
    conn, addr = s.accept()
    threading.Thread(target=handle_worker, args=(conn, addr), daemon=True).start()
