import select
import socket
import time

import interface
import random
import communication_manager as cl
import message_manager as msm


def Client():

    # server = srv.CommunicationManager('localhost', 5683)
    # messageId = int(random.random() * 210902)

    message = msm.Message(msm.Type.Confirmable, msm.Class.Method, msm.Method.GET)

    message.addMessageID(1234)
    message.addToken(0x8)
    message.addOption(8, 'home/')
    message.addOption(11, 'pingu/angelica')
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


if __name__ == '__main__':

    Client()

    # GUI = interface.Window()
    # GUI.title("CoAP - client")
    # GUI.mainloop()

