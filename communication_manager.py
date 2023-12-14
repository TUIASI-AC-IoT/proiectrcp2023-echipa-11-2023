import socket

class CommunicationManager:
    def __init__(self, ip, port):
        self.address = (ip, port)
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.__socket.bind(('0.0.0.0', 5683))

    def request(self, message):
        self.__socket.sendto(message, self.address)

