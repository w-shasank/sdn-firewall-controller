import json
from pathlib import Path

from os_ken.base import app_manager
from os_ken.controller import ofp_event
from os_ken.controller.handler import CONFIG_DISPATCHER, set_ev_cls
from os_ken.ofproto import ofproto_v1_3

RULES_FILE = Path(__file__).resolve().parent.parent / "config" / "firewall_rules.json"
PROTOCOLS = {"icmp": 1, "tcp": 6, "udp": 17}


class Firewall(app_manager.OSKenApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with open(RULES_FILE) as f:
            self.rules = json.load(f)
        self.logger.info("Loaded %d firewall rule(s)", len(self.rules))

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def install_rules(self, ev):
        dp = ev.msg.datapath
        parser = dp.ofproto_parser

        for rule in self.rules:
            fields = {"eth_type": 0x0800}
            if "protocol" in rule:
                fields["ip_proto"] = PROTOCOLS[rule["protocol"]]
            if "src_ip" in rule:
                fields["ipv4_src"] = rule["src_ip"]
            if "dst_ip" in rule:
                fields["ipv4_dst"] = rule["dst_ip"]
            if "dst_port" in rule:
                fields[rule["protocol"] + "_dst"] = rule["dst_port"]

            match = parser.OFPMatch(**fields)
            dp.send_msg(parser.OFPFlowMod(datapath=dp, priority=100,
                                          match=match, instructions=[]))
            self.logger.info("DROP rule installed: %s", rule.get("name", "unnamed"))