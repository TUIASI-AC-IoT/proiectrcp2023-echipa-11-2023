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
                    msg = msm.Message(msm.Type.Confirmable, msm.Class.Method, msm.Method.GET)
                    msg.decode(msg_received)
                    msg.displayMessage()
                    msg.addPayload(bytearray('Echo', encoding="ascii"))
                    send = msg.encode()
                    self.__socket.sendto(send, ('127.0.0.1', 49153))
        except KeyboardInterrupt:
            print("Server stopped by user.")
        finally:
            self.__socket.close()


server = Server('127.0.0.1', 5683)

server.communication()
