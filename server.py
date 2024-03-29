import select
import socket
from time import sleep

import message_manager as msm
from communication_manager import clientPort

class Server:

    def __init__(self, ip, port):
        self.address = (ip, port)
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.__socket.bind(self.address)
        self.files = 'dir:pingu|file:coco.txt|file:cica.txt'
        self.path = 'pinguini/'

    def communication(self):
        try:
            while True:
                print('in while')
                msg_received, addr = self.__socket.recvfrom(4096)
                if msg_received:
                    print(msg_received, end='1\n')
                    msg_received = bytearray(msg_received)
                    print(msg_received, end='2\n')
                    # buinding ack response
                    msg_received[0] = msg_received[0] & 0xDF | (msg_received[0] & 0x00 | 0x20)
                    print(msg_received, end='3\n')

                    sleep(1)

                    # daca mesajul nu e bun, returnam un mesaj de tip RST
                    try:
                        msg = msm.Message(msm.Type.Confirmable, msm.Class.Method, msm.Method.GET)
                        msg.decode(msg_received)
                        # prin1
                        if msg.messageCode == msm.Method.GET:
                            msg.messageCode = msm.Success.Content
                            msg.messageClass = msm.Class.Success
                            msg.addPayload(bytearray(self.files, 'ascii'))
                            msg.addOption(8, bytearray(self.path, 'ascii'))
                            send = msg.encode()
                            self.__socket.sendto(send, ('127.0.0.1', 49153))
                            continue
                        if msg.messageCode == msm.Method.PUT:
                            # modificam lista de fisiere pt rename
                            msg.messageCode = msm.Success.Changed
                            msg.messageClass = msm.Class.Success
                            msg.displayMessage()
                            oldF = msg.getOptionValue(msm.Options.LOCATION_PATH).decode()
                            newF = msg.getPayload().decode()
                            self.files = self.files.replace(oldF, newF)
                            msg.emptyOptions()
                            msg.emptyPayload()
                            msg.addPayload(bytearray(self.files, 'ascii'))
                            msg.addOption(8, bytearray(self.path, 'ascii'))
                            send = msg.encode()
                            self.__socket.sendto(send, ('127.0.0.1', 49153))
                            continue
                        if msg.messageCode == msm.Method.POST:
                            msg.messageCode = msm.Success.Created
                            msg.messageClass = msm.Class.Success
                            newF = msg.getPayload().decode()
                            self.files += '|'+newF
                            msg.emptyOptions()
                            msg.emptyPayload()
                            msg.addPayload(bytearray(self.files, 'ascii'))
                            msg.addOption(8, bytearray(self.path, 'ascii'))
                            send = msg.encode()
                            self.__socket.sendto(send, ('127.0.0.1', 49153))
                            continue
                        msg.displayMessage()
                        msg.addPayload(bytearray('Echo', encoding="ascii"))
                        send = msg.encode()
                        self.__socket.sendto(send, ('127.0.0.1', 49153))
                    except Exception as e:
                        # ceva ciudat aici la setarea versiunii?
                        # la decode in client da eroarea Invalid Version
                        # resolved
                        msg = msm.Message(msm.Type.Reset, msm.Class.Server_Error, msm.Method.EMPTY)
                        msg.addMessageID(1)
                        msg.addToken(0x1)
                        msg.addPayload(bytearray(f'Error: {e}', encoding="ascii"))
                        msg.displayMessage()
                        send = msg.encode()
                        self.__socket.sendto(send, ('127.0.0.1', 49153))
                        print(f'Error: {e}')


        except KeyboardInterrupt:
            print("Server stopped by user.")
        finally:
            self.__socket.close()


def ServerRun():
    server = Server('127.0.0.1', 5683)
    server.communication()

ServerRun()
