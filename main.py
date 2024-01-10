import queue
import select
import socket
import threading
import time
import interface
import communication_manager as cm
from communication_manager import CommunicationManager as CM

from server import ServerRun
# importul executa fisierul si stocheaza .pyc in pycache

import message_manager as msm


def Client():
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

if __name__ == '__main__':

    commandQ = queue.Queue()
    eventQ = queue.Queue()
    # server part
    threading.Thread(target=ServerRun, daemon=True).start()

    # client part
    threading.Thread(target=Client, daemon=True).start()

    # command listener
    # de mutat clientul in communication manager
    # cm = CM(commandQ, eventQ)
    # cm.ComLis()

    GUI = interface.Window(commandQ, eventQ)
    GUI.title("CoAP - client")
    GUI.mainloop()

