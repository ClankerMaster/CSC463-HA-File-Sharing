'''
Script for client side
@author: hao
'''

import protocol
import config
from socket import *
import os


class client:

    fileList = []

    # Constructor: load client configuration
    def __init__(self):
        (self.serverName,
         self.serverPort,
         self.clientPort,
         self.downloadPath,
         self.uploadPath) = config.config().readClientConfig()

        self.fileList = []

    # Function to produce user menu
    def printMenu(self):
        print("\nWelcome to simple file sharing system!")
        print("Please select operations from menu")
        print("--------------------------------------")
        print("1. Review the List of Available Files")
        print("2. Download File")
        print("3. Upload File")
        print("4. Quit")

    # Function to get user selection
    def getUserSelection(self):
        while True:
            self.printMenu()

            try:
                ans = int(input("Enter option: "))
            except ValueError:
                ans = 0

            if 1 <= ans <= 4:
                return ans

            print("Invalid Option")

    # Build connection to server
    def connect(self):
        clientSocket = socket(AF_INET, SOCK_STREAM)
        clientSocket.connect((self.serverName, self.serverPort))
        return clientSocket

    # Get file list from server
    def getFileList(self):
        mySocket = self.connect()

        try:
            mySocket.sendall(
                protocol.prepareMsg(protocol.HEAD_REQUEST, " ")
            )

            response = b""

            while True:
                data = mySocket.recv(4096)
                if not data:
                    break
                response += data

            header, msg = protocol.decodeMsg(response.decode())

            if header == protocol.HEAD_LIST:
                self.fileList = (
                    msg.split(",") if msg else []
                )
            else:
                print("Error: cannot get file list!")

        finally:
            mySocket.close()

    # Print files in the list
    def printFileList(self):
        if not self.fileList:
            print("No files available.")
            return

        count = 0
        for f in self.fileList:
            count += 1
            print('{:<3d}{}'.format(count, f))

    # Select file for downloading
    def selectDownloadFile(self):
        self.getFileList()

        if not self.fileList:
            print("No files available to download.")
            return None

        while True:
            self.printFileList()
            print("Please select the file you want to download:")

            try:
                ans = int(input("File number: "))
            except ValueError:
                ans = -1

            if 1 <= ans <= len(self.fileList):
                return self.fileList[ans - 1]

            print("Invalid number")

    # Download file from server
    def downloadFile(self, fileName):
        if not fileName:
            return

        os.makedirs(self.downloadPath, exist_ok=True)
        mySocket = self.connect()

        try:
            mySocket.sendall(
                protocol.prepareMsg(
                    protocol.HEAD_DOWNLOAD, fileName
                )
            )

            filePath = os.path.join(self.downloadPath, fileName)

            with open(filePath, 'wb') as f:
                while True:
                    data = mySocket.recv(4096)
                    if not data:
                        break
                    f.write(data)

            print(fileName + " has been downloaded!")

        finally:
            mySocket.close()

    # NEW: Upload file to server
    def upLoadFile(self, fileName):
        if not fileName:
            return

        filePath = os.path.join(self.uploadPath, fileName)

        if not os.path.isfile(filePath):
            print("Error: File does not exist!")
            return

        mySocket = self.connect()

        try:
            # Send upload request with filename
            mySocket.sendall(
                protocol.prepareMsg(
                    protocol.HEAD_UPLOAD, fileName
                )
            )

            # Wait for server to accept request
            response = mySocket.recv(1024)

            if response != b"READY":
                print("Server rejected upload request.")
                return

            # Send the actual file
            with open(filePath, 'rb') as f:
                while True:
                    data = f.read(4096)
                    if not data:
                        break
                    mySocket.sendall(data)

            # Tell server no more file data is coming
            mySocket.shutdown(SHUT_WR)

            # Wait for confirmation
            response = mySocket.recv(1024)

            if response == b"OK":
                print(fileName + " has been uploaded!")
            else:
                print("Upload was not confirmed by server.")

        finally:
            mySocket.close()

    # NEW: Select a file from upload folder
    def selectUploadFile(self):
        os.makedirs(self.uploadPath, exist_ok=True)

        files = [
            f for f in os.listdir(self.uploadPath)
            if os.path.isfile(os.path.join(self.uploadPath, f))
        ]

        if not files:
            print("No files available to upload.")
            return None

        print("\nFiles available for upload:")

        for i, f in enumerate(files, start=1):
            print(f"{i}. {f}")

        while True:
            try:
                ans = int(input("Select file number: "))
            except ValueError:
                ans = -1

            if 1 <= ans <= len(files):
                return files[ans - 1]

            print("Invalid number")

    # Main logic of the client
    def start(self):
        opt = 0

        while opt != 4:
            opt = self.getUserSelection()

            try:
                if opt == 1:
                    self.getFileList()
                    self.printFileList()

                elif opt == 2:
                    fileName = self.selectDownloadFile()
                    self.downloadFile(fileName)

                elif opt == 3:
                    fileName = self.selectUploadFile()
                    self.upLoadFile(fileName)

                elif opt == 4:
                    print("Goodbye!")

            except OSError as e:
                print("Network or file error:", e)


def main():
    c = client()
    c.start()


if __name__ == "__main__":
    main()
