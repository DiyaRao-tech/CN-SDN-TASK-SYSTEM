h1 pkill -f server.py
sh sleep 1
h1 python3 baseline/static_server.py 30 > /tmp/server.log 2>&1 &
sh sleep 1
h2 python3 worker/worker.py w1 10.0.0.1 1.0 > /tmp/w1.log 2>&1 &
h3 python3 worker/worker.py w2 10.0.0.1 1.0 > /tmp/w2.log 2>&1 &
h4 python3 worker/worker.py w3 10.0.0.1 3.0 > /tmp/w3.log 2>&1 &
