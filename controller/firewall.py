from os_ken.base import app_manager
from os_ken.controller import ofp_event
from os_ken.controller.handler import CONFIG_DISPATCHER, set_ev_cls
from os_ken.ofproto import ofproto_v1_3


class Firewall(app_manager.OSKenApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def install_rules(self, ev):
        dp = ev.msg.datapath
        parser = dp.ofproto_parser

        match = parser.OFPMatch(eth_type=0x0800, ip_proto=1,
                                ipv4_src="10.0.0.2", ipv4_dst="10.0.0.3")
        dp.send_msg(parser.OFPFlowMod(datapath=dp, priority=100,
                                      match=match, instructions=[]))
        self.logger.info("DROP rule installed: ICMP 10.0.0.2 -> 10.0.0.3")