#!/usr/bin/env python

import hpsdnclient as hp
import os

""" Duplex Mismatch Detection """

# Initialize the api
controller = os.getenv('SCA')
auth = hp.XAuthToken(user='sdn',password='skyline', server=controller)
api = hp.Api(controller=controller, auth=auth)

# The Class used to pretty print the port with CRC or Late Collisions
class Duplex_mismatch_port:
	def __init__(self, dpid, port, collisions, rx_crc_err):
		self.dpid = dpid
		self.port = port
		self.collisions = collisions
		self.rx_crc_err = rx_crc_err

	# Overwrite of the print function to simplify the code
	def __str__(self):
		return "=========" + os.linesep \
			+ "DPID: " + self.dpid + os.linesep \
			+ "Port: " + str(self.port) + os.linesep \
			+ "Late Collisions: " + str(self.collisions) + os.linesep \
			+ "CRC Errors: " + str(self.rx_crc_err)

def print_duplex_error(dpid, port, node, ext_1, ext_2):
	if len(node) != 0:
		print "It is possible that an auto-negocation problem occurs on the port " + str(port) + \
		      " from the switch " + dpid + " which goes to the node " + node[0].ip + "."
		print "The switch is probably in " + ext_1 + " and the host in " + ext_2 + "."
	else:
		print "Impossible to get the node ip address maybe the ARP table is empty."


# A list wich will be fill with created Duplex_mismatch_port
list_port_error = []

# List all the switch in the network
for datapath in api.get_datapaths():
	# List all the port of those switch
	for port in api.get_ports(datapath.dpid):
		# Get the stats for all ports
		for stats in api.get_port_stats(datapath.dpid, port.id):
			port_stats = stats.port_stats[0]
			if port_stats.collisions or port_stats.rx_crc_err is not 0:
				list_port_error.append(Duplex_mismatch_port(datapath.dpid, \
									    port.id, \
									    port_stats.collisions, \
									    port_stats.rx_crc_err))

# Printing the errors
if not list_port_error:
	print "No Collisions and CRC errors in this network"
else:
	for port_error in list_port_error:
		print port_error


# Analyze the list of errors
for port_error in list_port_error:
	node = api.get_nodes(dpid=port_error.dpid, port=port_error.port)
	if port_error.collisions is not 0:
		print_duplex_error(port_error.dpid, port_error.port, "half-duplex", "full-duplex")
		
	if port_error.rx_crc_err is not 0:
		print_duplex_error(port_error.dpid, port_error.port, "full-duplex", "half-duplex")
