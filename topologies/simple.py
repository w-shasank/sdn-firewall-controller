from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.node import OVSSwitch, RemoteController
from mininet.topo import Topo


class SimpleTopo(Topo):
    def build(self):
        s1 = self.addSwitch("s1", protocols="OpenFlow13")
        for i in (1, 2, 3):
            h = self.addHost(f"h{i}", ip=f"10.0.0.{i}/24",
                             mac=f"00:00:00:00:00:0{i}")
            self.addLink(h, s1)


def make_net():
    net = Mininet(topo=SimpleTopo(), switch=OVSSwitch, controller=None)
    net.addController("c0", controller=RemoteController,
                      ip="127.0.0.1", port=6653)
    return net


if __name__ == "__main__":
    setLogLevel("info")
    net = make_net()
    net.start()
    CLI(net)
    net.stop()