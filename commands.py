import message_manager as msm

# Tipul mesajului va fi default de tip Confirmable
CommunicationType = msm.Type.Confirmable


class Command:

    def __init__(self):

        self.message = None

    def details(self):

        return self.message


class Create(Command):

    def __init__(self, name):

        super().__init__()
        self.message = msm.Message(CommunicationType, msm.Class.Method, msm.Method.POST)

        # self.message.addOption(msm.Options.LOCATION_PATH, path)
        self.message.addPayload(bytearray(str(name), 'ascii'))


class Upload(Command):

    def __init__(self, path, file):
        super().__init__()

        self.message = msm.Message(CommunicationType, msm.Class.Method, msm.Method.POST)

        self.message.addOption(msm.Options.LOCATION_PATH, path)


class Rename(Command):
    """Rename option"""

    def __init__(self,new_name, old_name):
        super().__init__()
        self.message = msm.Message(CommunicationType, msm.Class.Method, msm.Method.PUT)

        self.message.addOption(msm.Options.LOCATION_PATH, old_name)

        self.message.addPayload(bytearray(str(new_name), 'ascii'))


class Move(Command):

    def __init__(self, path):

        super().__init__()

        self.message = msm.Message(CommunicationType, msm.Class.Method, msm.Method.PUT)

        self.message.addOption(msm.Options.LOCATION_PATH, path)


class Download(Command):

    def __init__(self, path):

        super().__init__()

        self.message = msm.Message(CommunicationType, msm.Class.Method, msm.Method.GET)

        self.message.addOption(msm.Options.LOCATION_PATH, path)


class ListDirectory(Command):
    """Displays all dirs from current path"""
    def __init__(self, path):

        super().__init__()
        print('\nListDirectory')
        self.message = msm.Message(CommunicationType, msm.Class.Method, msm.Method.GET)

        for item in path:
            self.message.addOption(msm.Options.LOCATION_PATH, item)


class GetData(Command):

    def __init__(self, path):

        super().__init__()

        self.message = msm.Message(CommunicationType, msm.Class.Method, msm.Method.HEAD)

        self.message.addOption(msm.Options.LOCATION_PATH, path)


class Delete(Command):

    def __init__(self, path):

        super().__init__()

        self.message = msm.Message(CommunicationType, msm.Class.Method, msm.Method.DELETE)

        self.message.addOption(msm.Options.LOCATION_PATH, path)

