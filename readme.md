# sdn-firewall-controller

A small SDN controller written with os-ken (a fork of Ryu). It runs a learning switch and a firewall on a Mininet network over OpenFlow 1.3.

## Topology

```
h1 10.0.0.1 ---+
               |
h2 10.0.0.2 ---+--- s1 (Open vSwitch) ---- controller (127.0.0.1:6653)
               |
h3 10.0.0.3 ---+   (h3 is the web server)
```

## What it does

- **Learning switch** (`controller/learning_switch.py`): learns which MAC address is on which port and installs forwarding rules in the switch.
- **Firewall** (`controller/firewall.py`): reads `config/firewall_rules.json` and installs drop rules at a higher priority than the forwarding rules.

Rules in the default config:

| Rule | Effect |
|------|--------|
| h2 to h3, ICMP | ping blocked |
| h1 to h3, TCP port 80 | web access blocked |

Everything else is allowed.

## Setup

Tested on Ubuntu 24.04.

```bash
sudo apt install mininet openvswitch-switch python3-venv
git clone git@github.com:w-shasank/sdn-firewall-controller.git
cd sdn-firewall-controller
python3 -m venv .venv
source .venv/bin/activate
pip install os-ken==3.1.1
```

## Run

Terminal 1, start the controller:

```bash
source .venv/bin/activate
osken-manager --verbose controller/learning_switch.py controller/firewall.py
```

Terminal 2, run the tests:

```bash
sudo mn -c
sudo python3 tests/run_tests.py
```

To explore by hand, run `sudo python3 topologies/simple.py` instead. This opens the Mininet prompt.

To look at the rules inside the switch:

```bash
sudo ovs-ofctl -O OpenFlow13 dump-flows s1
```git 