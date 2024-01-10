import socket
import threading
import time

import message_manager as msm
import commands
import random
import queue


serverIpAddress = '127.0.0.1'
serverPort = 5683
clientIpAddress = '127.0.0.1'
clientPort = 49153

# Confirmable by default
CommunicationType = msm.Type.Confirmable

# Path default
DownloadDirectory = "Downloads/"


class CommunicationManager:

    TIMEOUT = 2
    MAX_RETRANSMIT = 4
    RANDOM_FACTOR = 5

    # block size is between 16 and 1024 bytes
    MAX_SIZE = 6
    MAX_BLOCK = 1 << (MAX_SIZE + 4)

    messageIdValue = random.randint(0, 0xFFFF)
    tokenValue = random.randint(0, 0XFFFF_FFFF)

    def __init__(self, commandQ: queue.Queue, eventQ: queue.Queue):
        self.address = (clientIpAddress, clientPort)
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.__socket.bind(self.address)

        self.commandQ = commandQ
        self.eventQ = eventQ

    def request(self, message):
        self.__socket.sendto(message, self.address)

    def response(self, message):
        pass

    def ComLis(self):
        threading.Thread(target=self.Client(), daemon=True).start()
        threading.Thread(target=self.commandListener(), daemon=True).start()

    def commandListener(self):
        print('\nComunicationManager, commandListener')
        """Takes the commands from commandQ and puts them in requestQ"""
        while True:
            # luam commanda din lista de comenzi
            command = self.commandQ.get()
            # var: var_type = value, where type(value) is var_type
            message: msm.Message = command.details()    # extragem mesajul

            self.request(message)

            self.commandQ.task_done()

    def Client(self):

        message = msm.Message(msm.Type.Confirmable, msm.Class.Method, msm.Method.GET)

        message.addMessageID(1234)
        message.addToken(0x8)
        message.addOption(8, 'home/')
        message.addOption(11, 'pingu/angelica')
        message.addOption(23, 1000)
        message.addOption(23, 2001)
        message.addPayload(bytearray('pinguuu', 'ascii'))
        message.displayMessage()
        # server.request(message.encode())
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        client.bind(('127.0.0.1', 49153))

        for i in range(10):
            try:
                print(message.encode())
                # message.displayMessage()
                client.sendto(message.encode(), ('127.0.0.1', 5683))
                # read, _, _ = select.select([client], [], [], 1)
                # if read:
                data, _ = client.recvfrom(4096)
                data = bytearray(data)
                msg = msm.Message()
                msg.decode(data)
                msg.displayMessage()
            except Exception as e:
                print(f'Error: {e}')

            time.sleep(1)
        client.close()
