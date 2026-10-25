from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch, Node
from mininet.topo import Topo
from mininet.cli import CLI

class TaskTopo(Topo):
    def build(self):
        s1 = self.addSwitch('s1', protocols='OpenFlow10')
        for i in range(1, 5):
            h = self.addHost('h%d' % i, ip='10.0.0.%d/24' % i)
            self.addLink(h, s1)

if __name__ == '__main__':
    net = Mininet(topo=TaskTopo(), controller=None, switch=OVSSwitch)
    net.addController('c0', controller=RemoteController,
                      ip='127.0.0.1', port=6633)
    root = Node('root', inNamespace=False)
    intf = net.addLink(root, net.get('s1')).intf1
    root.setIP('10.0.0.100/24', intf=intf)
    net.start()
    CLI(net)
    net.stop()
