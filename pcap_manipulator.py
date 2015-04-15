#!/usr/bin/env python

import sys, os, argparse, re, json, copy
from pprint import pprint
from scapy.all import *

mapping = {
'2001:470:e5bf:dead:4957:2174:e82c:4887':'10.21.74.87',
'2607:f8b0:400c:c03::1a':'10.40.25.1',
'fe80::1':'10.21.74.1',
'fe80::2':'10.21.74.2',
'ff02::1:ff00:1':'10.40.25.3',
}

def parse_arguments():

	parser = argparse.ArgumentParser()
	parser.add_argument('-r', '--pcap', help='PCAP file path')
	args = parser.parse_args()

	if len(sys.argv) < 2:
		parser.print_help()
		sys.exit(3)

	return args
	
# Not used ATM, but translation logic could be set here if we build IP4 from IP6
def translateIP6toIP4 (addr):
	
	ip4_addr = mapping.get(addr)

	return ip4_addr

def main():

	args = parse_arguments()
	pcapfile = args.pcap

	pkts = rdpcap(pcapfile)

	pktdump = PcapWriter("/tmp/new.pcap", append=True, sync=True)

	for packet in pkts:
		if (packet.haslayer(IPv6)):

			ipv6_src_mac = packet.getlayer(Ether).src
			ipv6_dst_mac = packet.getlayer(Ether).dst

			ipv6_src_addr = packet.getlayer(IPv6).src
			ipv6_dst_addr = packet.getlayer(IPv6).dst
			ipv6_proto = packet.getlayer(IPv6).nh
			ipv6_len = packet.getlayer(IPv6).plen


			ipv4_src_addr = mapping.get(ipv6_src_addr)
			ipv4_dst_addr = mapping.get(ipv6_dst_addr)

			newpacket = Ether(src=ipv6_src_mac, dst=ipv6_dst_mac, type=0x800)/IP(src=ipv4_src_addr, dst=ipv4_dst_addr, proto=ipv6_proto, len=ipv6_len)/packet.getlayer(IPv6).payload
			#newpacket = Ether(src=ipv6_src_mac, dst=ipv6_dst_mac, type=ipv6_type)
			#newpacket = newpacket/IP(src=ipv4_src_addr, dst=ipv4_dst_addr, proto=ipv6_proto, len=ipv6_len)/packet.getlayer(IPv6).payload

			pktdump.write(newpacket)

			# Debug section
			print '---------------------------------------'
			newpacket.show2()
#			print ipv4_src_addr
#			print ipv4_dst_addr

if __name__ == "__main__":

        main()
