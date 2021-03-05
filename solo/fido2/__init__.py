import os
import socket

import fido2.hid
from fido2.hid.base import CtapHidConnection, HidDescriptor


def force_udp_backend():
    fido2.hid.list_descriptors = list_descriptors
    fido2.hid.get_descriptor = get_descriptor
    fido2.hid.open_connection = open_connection


def open_connection(descriptor):
    return UDPHidConnection(descriptor)


class UDPHidConnection(CtapHidConnection):
    def __init__(self, descriptor):
        breakpoint()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("127.0.0.1", 7112))
        addr, port = descriptor.path.split(":")
        port = int(port)
        self.token = (addr, port)
        self.sock.settimeout(1.0)

    def close(self):
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()

    def write_packet(self, packet):
        self.sock.sendto(bytearray(packet), self.token)

    def read_packet(self):
        msg = [0] * 64
        pkt, _ = self.sock.recvfrom(64)
        for i, v in enumerate(pkt):
            try:
                msg[i] = ord(v)
            except TypeError:
                msg[i] = v
        return msg


class SoloUDPDescriptor(HidDescriptor):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.product_string = "software test interface"
        self.serial_number = "12345678"


def get_descriptor(path):
    path = "localhost:8111"
    vid = 0x1234
    pid = 0x5678
    max_in_size = max_out_size = 64
    return [SoloUDPDescriptor(path, vid, pid, max_in_size, max_out_size)]


def list_descriptors():
    return get_descriptor(None)
