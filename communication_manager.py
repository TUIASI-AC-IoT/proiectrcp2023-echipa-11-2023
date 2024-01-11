import select
import socket
import threading
import time

import events
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

        self.sendLock = threading.Lock()

        # coada pentru rasunsuri
        self.responseQ = queue.Queue()

        # lista pentru requesturi
        self.requestList = []

    def request(self, message):
        print('\nCommunicationManager, request')
        # blocam resursa pentru a ne asigura ca este utilizata coresounzator
        with self.sendLock:
            self.__socket.sendto(message, (serverIpAddress, serverPort))

    def startThreading(self):
        """Starts the message managing threads"""
        # should we use join() ?
        # threading.Thread(target=self.Client(), daemon=True).start()
        threading.Thread(target=self.responseListener, daemon=True).start()
        threading.Thread(target=self.responseSolver, daemon=True).start()
        threading.Thread(target=self.commandListener, daemon=True).start()

    def commandListener(self):
        """Takes the commands from commandQ and puts them in requestQ"""
        print('\nComunicationManager, commandListener')
        while True:
            # luam commanda din lista de comenzi
            print('pingu?')
            command = self.commandQ.get()
            self.commandQ.task_done()
            # var: var_type = value, where type(value) is var_type
            message: msm.Message = command.details()    # extragem mesajul

            # construim mesajul (add la id si la token)
            message.addMessageID(self.messageIdValue)
            message.addToken(self.tokenValue)
            message.displayMessage()
            self.request(message.encode())

            # incrementam id is token pentru urilizarile ulterioare ale instantei
            self.messageIdValue += 1
            self.tokenValue += 1

            # salvam datele despre mesaj in lista de mesaje
            self.requestList.append((message, time.time(), self.TIMEOUT, self.MAX_RETRANSMIT))
            print(self.requestList)

    def responseListener(self):
        """Reads data, if is any data available on the socket => decodes the data and ads it to the response queue"""
        print('\nCommunicationManager, responseListener')
        while True:
            # check if there is data available for reading on the socket
            # https://docs.python.org/3/library/select.html
            read, _, _ = select.select([self.__socket], [], [], 1)     # kinda an interface to select()-UNIX system call
            if read:
                data, _ = self.__socket.recvfrom(4096)
                message = msm.Message()
                message.decode(bytearray(data))
                message.displayMessage()
                self.responseQ.put(message)

    def responseSolver(self):
        """Solutioneaza raspunsurile venite de la server"""
        print('\nCommunicationManager, responseSolver')
        while True:
            response: msm.Message = self.responseQ.get()     # ia mesajul din coada de responses
            self.responseQ.task_done()
            print(type(response))

            request = None      # requestul asociat responsului
            if response.token is None:
                # request = msm.Message(msm.Type.Reset, msm.ClientError.Not_Found, )
                continue
            elif response.token == 0:
                # tokenul e null
                continue
            else:
                # tokenul e bun, facem mathing cu tokenul din request ca sa il stergem
                for msg in self.requestList:
                    if response.token == msg[0].token:
                        request = msg[0]       # am gasit requestul
                        request.displayMessage()
                        break
                if request is None:
                    continue    # nu am gasit requestul
                response.displayMessage()
                # triggering events based on responses
                if response.messageClass == msm.Class.Success:  # response is SUCCESS
                    # REQUEST = GET and RESPONSE = SUCCESS.CONTENT  TODO: SUCCES.VALID
                    if request.messageCode == msm.Method.GET and response.messageCode == msm.Success.Content:
                        # optiunea content_format are valoarea plain text
                        # luam din payload lista de fisiere/directoare
                        print('print resposes')
                        data = response.getPayload().decode()
                        files1 = data.split('|')
                        files2 = []
                        for item in files1:
                            files2.append(tuple(item.split(':')))
                        path = response.getOptionValue(msm.Options.LOCATION_PATH).decode()
                        self.eventQ.put(events.Event(events.EventType.FILE_LIST, (files2, path)))

                if request.messageCode == msm.Method.PUT and response.messageCode == msm.Success.Changed:
                    # file rename
                    print('rename')
                    data = response.getPayload().decode()
                    files1 = data.split('|')
                    files2 = []
                    for item in files1:
                        files2.append(tuple(item.split(':')))
                    path = response.getOptionValue(msm.Options.LOCATION_PATH).decode()
                    self.eventQ.put(events.Event(events.EventType.FILE_LIST, (files2, path)))

                if request.messageCode == msm.Method.POST and response.messageCode == msm.Success.Created:
                    # create file event
                    data = response.getPayload().decode()
                    files1 = data.split('|')
                    files2 = []
                    for item in files1:
                        files2.append(tuple(item.split(':')))
                    path = response.getOptionValue(msm.Options.LOCATION_PATH).decode()
                    self.eventQ.put(events.Event(events.EventType.FILE_LIST, (files2, path)))



    # def Client(self):
    #
    #     message = msm.Message(msm.Type.Confirmable, msm.Class.Method, msm.Method.GET)
    #
    #     message.addMessageID(1234)
    #     message.addToken(0x8)
    #     message.addOption(8, 'home/')
    #     message.addOption(11, 'pingu/angelica')
    #     message.addOption(23, 1000)
    #     message.addOption(23, 2001)
    #     message.addPayload(bytearray('pinguuu', 'ascii'))
    #     message.displayMessage()
    #     # server.request(message.encode())
    #     client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    #     client.bind(('127.0.0.1', 49153))
    #
    #     for i in range(10):
    #         try:
    #             print(message.encode())
    #             # message.displayMessage()
    #             client.sendto(message.encode(), ('127.0.0.1', 5683))
    #             # read, _, _ = select.select([client], [], [], 1)
    #             # if read:
    #             data, _ = client.recvfrom(4096)
    #             data = bytearray(data)
    #             msg = msm.Message()
    #             msg.decode(data)
    #             msg.displayMessage()
    #         except Exception as e:
    #             print(f'Error: {e}')
    #
    #         time.sleep(1)
    #     client.close()
