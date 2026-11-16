'''
Script for server
@author: hao
'''

import config
import protocol
import os
from socket import *


class server:

    # Constructor: load the server information from config file
    def __init__(self):
        self.port, self.path = config.config().readServerConfig()

    # Get the file names from shared directory
    def getFileList(self):
        return [
            f for f in os.listdir(self.path)
            if os.path.isfile(os.path.join(self.path, f))
        ]

    # Function to send file list to client
    def listFile(self, serverSocket):
        serverSocket.sendall(
            protocol.prepareFileList(
                protocol.HEAD_LIST, self.getFileList()
            )
        )

    # Function to send a file to client
    def sendFile(self, serverSocket, fileName):
        fileName = os.path.basename(fileName)
        filePath = os.path.join(self.path, fileName)

        if not os.path.isfile(filePath):
            print("File not found:", fileName)
            return

        with open(filePath, 'rb') as f:
            while True:
                data = f.read(4096)
                if not data:
                    break
                serverSocket.sendall(data)

        print("File downloaded by client:", fileName)

    # NEW: Receive uploaded files from client
    def receiveFile(self, connectionSocket, fileName):
        if not fileName or fileName != os.path.basename(fileName):
            connectionSocket.sendall(b"ERROR")
            return

        filePath = os.path.join(self.path, fileName)

        # Tell the client the server is ready
        connectionSocket.sendall(b"READY")

        # Receive file data
        with open(filePath, 'wb') as f:
            while True:
                data = connectionSocket.recv(4096)
                if not data:
                    break
                f.write(data)

        print("File uploaded successfully:", fileName)

        # Confirm completion
        connectionSocket.sendall(b"OK")

    # Main function of server, start the file sharing service
    def start(self):
        serverPort = self.port
        serverSocket = socket(AF_INET, SOCK_STREAM)
        serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        serverSocket.bind(('', serverPort))
        serverSocket.listen(20)

        print('The server is ready to receive')

        while True:
            connectionSocket, addr = serverSocket.accept()

            try:
                dataRec = connectionSocket.recv(1024)
                if not dataRec:
                    continue

                header, msg = protocol.decodeMsg(dataRec.decode())

                # Main logic of the program
                if header == protocol.HEAD_REQUEST:
                    self.listFile(connectionSocket)

                elif header == protocol.HEAD_DOWNLOAD:
                    self.sendFile(connectionSocket, msg)

                elif header == protocol.HEAD_UPLOAD:
                    self.receiveFile(connectionSocket, msg)

                else:
                    connectionSocket.sendall(
                        protocol.prepareMsg(
                            protocol.HEAD_ERROR, "Invalid Message"
                        )
                    )

            except Exception as e:
                print("Error handling client:", e)

            finally:
                connectionSocket.close()


def main():
    s = server()
    s.start()


if __name__ == "__main__":
    main()
