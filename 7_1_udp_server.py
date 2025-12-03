#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 22 14:57:38 2025

@author: Ruian Zhao
"""

import socket

# Note the address
SERVER_IP_ADDRESS = "127.0.0.1"
PORT = 2024

# Create the socket
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((SERVER_IP_ADDRESS, PORT))

path_to_image_copy = "/Image_Copy_Path"

print(f"The UDP server is available on << {SERVER_IP_ADDRESS}:{PORT} >>")

# Receive the image
expected_id = 0
image = b''

# This loop will keep receiving packets from the client until it recieves
# a packet with an empty payload where it will exit the loop
while True:
    packet, client_address = server.recvfrom(16384)
    received_id = int.from_bytes(packet[0:4], 'big')
    
    # Checks if the payload is empty
    if (len(packet[4:]) == 0):
        # Sending this ack with an id longer than the payload length will 
        # tell the client to terminate
        expected_id = expected_id + 1
        ack = expected_id.to_bytes(4, 'big')
        server.sendto(ack, client_address)
        break
    # If the id recieved is the one expected, append the payload to the image
    # and increment the id for the ack and send the ack back to the client
    elif (received_id == expected_id):
        image = image + packet[4:]
        expected_id = expected_id + 1
        ack = expected_id.to_bytes(4, 'big')
        server.sendto(ack, client_address)
    # Otherwise the wrong packet id was sent and request a retransmission
    else:
        ack = expected_id.to_bytes(4, 'big')
        server.sendto(ack, client_address)


with open(path_to_image_copy, 'wb') as file:
    file.write(image)