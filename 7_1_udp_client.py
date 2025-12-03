#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 22 14:57:30 2025

@author: Ruian Zhao
"""

import socket

# Note the address and paths
SERVER_IP_ADDRESS = "127.0.0.1"
PORT = 2024
path_to_image = "/Image_Path"

# Get the image as the message
with open(path_to_image, 'rb') as image: 
    image_bytes = image.read()
    
payload = []
id = 0

# This loop iterates through the image and splits it into chunks of 1000 bytes
# and appends it to the payload list
for byte in range(0, len(image_bytes), 1000):
    # We prepend the id of the chunk so when the server gets the data we can decode its id
    id_header = id.to_bytes(4, 'big')
    packet = id_header + image_bytes[byte: byte + 1000]
    payload.append(packet)
    id = id + 1

#Add a payload with just the id and no image bytes to signal to server the end of the image
id_header = id.to_bytes(4, 'big')
payload.append(id_header)
    
# Create socket
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:
    # Try to send the image to the server 
    
    print("The UDP Client is going to send a message...")
    
    client.settimeout(0.5)
        
    current_id = 0
    window_size = 1
    total_chunks = len(payload)
    
    # Send as many chunks as the window size
    while current_id < total_chunks:
        try:
            for i in range(window_size): 
                if current_id + i < total_chunks:
                    client.sendto(payload[current_id + i], (SERVER_IP_ADDRESS, PORT))
            
            last_ack_received = current_id
            
            # We loop until we get the ack for the last packet
            # we sent OR the socket times out.
            while True:
                try:
                    client.settimeout(0.1) 
                    ack_data, _ = client.recvfrom(1024)
                    received_next_id = int.from_bytes(ack_data, 'big')
                    
                    # Update our most recent ACK id
                    if received_next_id > last_ack_received:
                        last_ack_received = received_next_id
                        
                    # If we get an ack for every packet sent stop waiting
                    if last_ack_received >= current_id + window_size:
                        break
                
                # If the packets get lost        
                except socket.timeout:
                    break
            
            # If we received an ack for every transmitted packet we can double
            # the window size and update the id for the next packet to transmit
            if last_ack_received >= current_id + window_size:
                current_id = last_ack_received
                window_size = window_size * 2
            
            # If we successfully transmitted some packets but not all, reset the window 
            # size and update the next id to be transmit
            elif last_ack_received > current_id:
                 current_id = last_ack_received
                 window_size = 1
                 
            # If no better acks were received reset the window size and retransmit
            else:
                window_size = 1
        
        # This runs when a packet gets lost
        except socket.timeout:
            print(f"Timeout! Resending...")      
        
        except socket.error as err:
            print(str(err))

        
            
    