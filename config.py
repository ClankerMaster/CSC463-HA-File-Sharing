'''
This is the file to read configuration files

Server configuration:
SERVER_PORT=SERVER_PORT_NUMBER
PATH=PATH_OF_SERVER_SHARED_DIRECTORY

Client configuration:
SERVER=SERVER_HOSTNAME/IP
SERVER_PORT=SERVER_PORT_NUMBER
CLIENT_PORT=CLIENT_PORT_NUMBER
DOWNLOAD=PATH_OF_CLIENT_DOWNLOAD_DIRECTORY
UPLOAD=PATH_OF_CLIENT_UPLOAD_DIRECTORY

@author: hao
'''


class config:

    # Define headers
    server_port = 'SERVER_PORT'
    path = 'PATH'
    server = 'SERVER'
    client_port = 'CLIENT_PORT'
    download = 'DOWNLOAD'
    upload = 'UPLOAD'

    serverConfig = "server.config"
    clientConfig = "client.config"

    def __init__(self):
        pass

    def readServerConfig(self):
        serPort = 0
        sharePath = ""

        with open(self.serverConfig, 'r') as f:
            for l in f:
                sub = l.strip().split("=", 1)

                if len(sub) != 2:
                    continue

                if sub[0] == self.server_port:
                    serPort = int(sub[1])

                elif sub[0] == self.path:
                    sharePath = sub[1]

        return serPort, sharePath

    def readClientConfig(self):
        '''
        Read client configuration file

        Return:
        serverName
        serverPort
        clientPort
        downloadPath
        uploadPath
        '''

        serPort = 0
        serName = ""
        clientPort = 0
        downPath = ""
        upPath = ""

        with open(self.clientConfig, 'r') as f:
            for l in f:
                sub = l.strip().split("=", 1)

                if len(sub) != 2:
                    continue

                if sub[0] == self.server_port:
                    serPort = int(sub[1])

                elif sub[0] == self.server:
                    serName = sub[1]

                elif sub[0] == self.client_port:
                    clientPort = sub[1]

                elif sub[0] == self.download:
                    downPath = sub[1]

                elif sub[0] == self.upload:
                    upPath = sub[1]

        return serName, serPort, clientPort, downPath, upPath


# Function to test configuration class
def test():
    conf = config()
    clientInfo = conf.readClientConfig()
    serverInfo = conf.readServerConfig()

    print(clientInfo)
    print(serverInfo)
