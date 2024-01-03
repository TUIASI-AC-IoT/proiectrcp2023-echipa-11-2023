import socket
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
                msg = msm.Message(msm.Type.Confirmable, msm.Class.Method, msm.Method.GET)
                msg_received, addr = self.__socket.recvfrom(1024)
                if not msg_received:
                    print('mesajul nu a fost primit')
                    break
                msg.decode(bytearray(msg_received))
                msg.displayMessage()
                # send = msg.encode()
                # self.__socket.sendto(send, ('127.0.0.1', clientPort))
        except KeyboardInterrupt:
            print("Server stopped by user.")
        finally:
            self.__socket.close()


server = Server('localhost', 5683)

server.communication()
