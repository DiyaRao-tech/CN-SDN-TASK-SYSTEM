import socket, threading, json, queue, time, sys

HOST, PORT = "0.0.0.0", 5000
CONTROLLER = ("10.0.0.100", 9999)
TASK_TIMEOUT = 5
NUM_TASKS = int(sys.argv[1]) if len(sys.argv) > 1 else 30

tasks = queue.Queue()
for i in range(1, NUM_TASKS + 1):
    tasks.put({"type": "TASK", "id": i, "data": i})

lock = threading.Lock()
workload = {}
done_count = 0
start_time = None

def notify(event, ip):
    try:
        c = socket.create_connection(CONTROLLER, timeout=2)
        c.sendall(("%s %s\n" % (event, ip)).encode())
        c.recv(16)
        c.close()
        print("Notified controller:", event, ip, flush=True)
    except OSError as e:
        print("Controller notify failed:", e, flush=True)

def handle_worker(conn, addr):
    global done_count, start_time
    ip = addr[0]
    f = conn.makefile("rw")
    conn.settimeout(TASK_TIMEOUT)
    name = "?"
    try:
        name = json.loads(f.readline())["name"]
        with lock:
            workload[name] = 0
        print("Registered", name, ip, flush=True)
        notify("WORKER_UP", ip)
        while done_count < NUM_TASKS:
            try:
                task = tasks.get(timeout=0.5)
            except queue.Empty:
                continue
            if start_time is None:
                start_time = time.time()
            try:
                f.write(json.dumps(task) + "\n")
                f.flush()
                line = f.readline()
                if not line:
                    raise ConnectionError("closed")
                reply = json.loads(line)
            except (OSError, ValueError):
                tasks.put(task)
                print("Worker", name, "failed; task", task["id"], "requeued", flush=True)
                notify("WORKER_DOWN", ip)
                return
            with lock:
                workload[name] += 1
                done_count += 1
                finished = (done_count == NUM_TASKS)
            print("Task", task["id"], "done by", name, "result", reply["result"], flush=True)
            if finished:
                print("ALL DONE in %.2f s" % (time.time() - start_time), workload, flush=True)
        f.write(json.dumps({"type": "DONE"}) + "\n")
        f.flush()
    except (OSError, ValueError):
        pass
    finally:
        conn.close()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen()
print("Server listening on port", PORT, "with", NUM_TASKS, "tasks", flush=True)
while True:
    conn, addr = s.accept()
    threading.Thread(target=handle_worker, args=(conn, addr), daemon=True).start()
