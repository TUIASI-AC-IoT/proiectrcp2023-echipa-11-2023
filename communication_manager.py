import socket
import message_manager as msm
import random



serverIpAddress = ''
serverPort = 5683
clientPort = 49153

# Confirmable by default
CommunicationType = msm.Type.Confirmable

# Path default
DownloadDirectory = "Downloads/"


class CommunicationManager:

    TIMEOUT = 2
    MAX_RETRANSMIT = 4
    RANDOM_FACTOR = 5

    MAX_SIZE = 6
    MAX_BLOCK = 1 << (MAX_SIZE + 4)

    messageIdValue = random.randint(0, 0xFFFF)
    tokenValue = random.randint(0, 0XFFFF_FFFF)

    def __init__(self, ip, port):
        self.address = (ip, port)
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.__socket.bind(('0.0.0.0', clientPort))

    def request(self, message):
        self.__socket.sendto(message, self.address)

