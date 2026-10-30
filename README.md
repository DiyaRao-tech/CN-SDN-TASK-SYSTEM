# CN-SDN-TASK-SYSTEM
# Distributed Task Notification and Worker System

Computer Networks mini-project 29 
A TCP task server hands tasks to workers inside a Mininet network. An SDN controller (POX) blocks a failed worker at the switch.

## How it works
- server/server.py: task queue, one thread per worker, 5 s timeout, re-queues a task if its worker fails, sends WORKER_UP / WORKER_DOWN to the controller.
- worker/worker.py: registers with the server, squares the number it is given, returns the result.
- controller/task_controller.py: POX component. Listens on TCP 9999 and installs or removes a drop rule (priority 40000) on switch s1.
- topology/topo.py: Mininet topology, one switch s1 and hosts h1 to h4 (10.0.0.1 to 10.0.0.4), remote controller on 127.0.0.1:6633, controller-side interface 10.0.0.100.
- tests/: normal.cmd, kill_worker.cmd, slow_worker.cmd.

## Ports
- 5000: tasks and results (server to workers)
- 6633: OpenFlow (switch to controller)
- 9999: server events to the controller

## Requirements
Ubuntu 25.04, Python 3, Mininet, Open vSwitch, POX 0.7.0 (cloned into ~/pox).

## How to run
1. Copy the controller into POX:
   cp controller/task_controller.py ~/pox/ext/
2. Terminal 1, start the controller:
   cd ~/pox
   python3 -u pox.py log.level --DEBUG forwarding.l2_learning task_controller
3. Terminal 2, start the network:
   sudo mn -c
   cd ~/CN-SDN-TASK-SYSTEM
   sudo python3 topology/topo.py
4. In the Mininet prompt, run a test:
   source tests/normal.cmd
   h1 tail -3 /tmp/server.log
5. Other tests:
   source tests/kill_worker.cmd
   source tests/slow_worker.cmd
6. Terminal 3, check the switch:
   sudo ovs-vsctl show
   sudo ovs-ofctl dump-flows s1

## Test results
| Test | Setup | Result |
| --- | --- | --- |
| Normal run | 3 workers, 1 s per task, 30 tasks | 11.20 s, split 10 / 10 / 10 |
| Worker failure | w2 killed after 3 s | 14.61 s, task re-queued, drop rule installed |
| Slow worker | w3 takes 3 s per task | 15.02 s, split 13 / 12 / 5 |

## Known limitation
A blocked worker cannot rejoin until the server sends WORKER_UP.

## Documentation
See docs/ for the report and screenshots.
