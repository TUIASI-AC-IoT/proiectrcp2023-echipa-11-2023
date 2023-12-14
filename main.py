import interface
import random
import communication_manager as srv, message_manager as msm


def Application():

    server = srv.CommunicationManager('localhost', 5683)

    messageId = int(random.random() * 210902)

    message = msm.Message(msm.Type.Confirmable, msm.Class.Method, msm.Method.GET)

    message.addOption(8, 'home/')

    server.request(message.encode())

if __name__ == '__main__':

    #Application()

    GUI = interface.Window()
    GUI.title("CoAP - client")
    GUI.mainloop()

