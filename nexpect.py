'''
nexpect.py
Authors: Josh Christman and Nathan Hart
Version: 1.0.1
Date: 6 July 2013

Changelog (v1.0.1):
    - Added default parameter to nexpect.sendline
        - Allows the method to be called as nexpect.sendline() instead of nexpect.sendline('')

Changelog (v1.0):
    - Added lots of comments
    - Added a spawn method
    - Changed the class name from SocketInteract to nexpect (Socket Expect)
    - Added ability to pass a tuple for connection information instead of a socket object
    - Added a timeout to the class that defaults to 30 seconds.
    - Changed the function name "sendLine" to "sendline" to match pexpect function name
    - Changed the expect method to return only data instead of tuple if a list of regexes was not passed into function
    - Added timeout code to the expect method that will correctly change the socket timeout value based on how much time is left in class timeout
    - Fixed the regex for loop so that it actually works
    - Added optional parameters to expect method
        - recvsize: changes the size of each socket receive in the while loop
        - timeout: a local override to the class wide timeout if user wants a specific timeout on a specific call to expect
    - Added function nexpect.settimeout()
    - Added shutdown and start methods
    - Tested github
'''

import threading,sys,socket,re,time

def spawn(sock, timeout=30):
    return nexpect(sock, timeout=timeout)

'''
The class nexpect is a socket expect module written using basic python modules. It should work on any
system with Python 2.7
'''
class nexpect():
    '''
    The constructor has one mandatory parameter:
        sock - This can be either a tuple with an address and port to connect to, or a socket object.
        Ex: s = nexpect(('www.example.com',1234))
        
            s = nexpect(('123.123.123.123',1234))

            sock = socket.socket()
            sock.connect(('www.example.com',1234))
            s = nexpect(sock)

    Optional parameters are:
        timeout - Sets the class timeout variable used as the timeout for the expect method
    '''
    def __init__(self, sock, timeout=30):
        self.timeout = timeout
        if type(sock) == type(()):
            self.socket = socket.socket()
            self.socket.connect(sock)
        elif type(sock) == type(socket.socket()):
            self.socket = sock
        else:
            raise TypeError

    '''
    This method does nothing but call the send method of the socket and pass the data to the socket
    '''
    def send(self, data=''):
        self.socket.sendall(data)

    '''
    This method appends a delimeter to the data and then sends it to the socket

    Optional parameters are:
        delimeter - Defaults to a '\n' but can be set to anything
    '''
    def sendline(self, data='', delimeter='\n'):
        self.socket.sendall(data + delimeter)

    '''
    This function takes a single regex in string form or a list/tuple of string regexes and receives data
    on the socket until it matches the regex. If a single regex is passed in, only the data received is
    returned from the function. If a list/tuple of regexes is passed in, the function returns a tuple of
    the data and the index of the regex it matched.

    Optional parameters are:
        recvsize - the size of the data to receive each time through the loop. It defaults to 1 but can
        be slow this way. Increase this if you know that the data being sent to you will be fairly regular.

        timeout - a local timeout override to the class variable timeout. This can be used for a time when
        you want a different timeout than the normal.
    '''
    def expect(self, regex, recvsize=1, timeout=0):
        isList = False
        if type(regex) == type(()) or type(regex) == type([]):
            isList = True

        data = ''
        t0 = time.time()
        while True:
            t1 = time.time()
            elapsedTime = t1-t0                 # Get the elapsed time since before the receive loop started
            if not timeout == 0:                # If there is a local timeout override as function parama=eter
                if elapsedTime > timeout:       # Test that instead
                    raise TimeoutException()
                else:    # If it hasn't timed out, set the socket's timeout so that it won't block forever
                    self.socket.settimeout(timeout - elapsedTime)
            elif elapsedTime > self.timeout:    # Else test the object's timeout
                raise TimeoutException()
            else:   # If it hasn't timed out, set the socket's timeout so that it won't block forever
                self.socket.settimeout(self.timeout - elapsedTime)

            try:
                data += self.socket.recv(recvsize)  # Receive bytes
            except:
                raise TimeoutException()
            
            if isList:                                  # Check if a list or tuple of regexes was passed in
                for counter,reg in enumerate(regex):    # Enumerate the regexes for testing
                    if re.search(reg, data):
                        return data, counter            # Return the data and the index of the regex found
            else:
                if re.search(regex, data):              # If only a single regex was passed in, return the data if it is found
                    return data

    '''
    The interact method makes this into a netcat-like functionality. It will print whatever it receives
    over the socket and send everything you type.

    Optional parameters are:
        delimeter - Specify a delimeter to be appended to all data sent over the socket. Defaults to a '\n'
    '''
    def interact(self, delimiter="\n"):
        try:
            r = self.recieverPrinter(self.socket)
            r.daemon = True # ensure the thread quits when the main thread dies
            r.start() # start the reciever thread
            # enter the send loop
            while True:
                command = raw_input()
                if command == "exit":
                    # die in a pretty manner
                    r.kill()
                    self.socket.sendall(command+delimiter)
                    return
                self.socket.sendall(command+delimiter)
        except KeyboardInterrupt:
            r.kill()
            return
        except:
            pass

    def settimeout(self, timeout):
        self.timeout = timeout

    def start(self, connection_data):
        self.socket = socket.socket()
        self.socket.connect(connection_data)

    def shutdown(self):
        self.socket.close()
        self.socket = None
                        
    class recieverPrinter(threading.Thread):
        def __init__(self, socket):
            super(nexpect.recieverPrinter, self).__init__()
            self.socket = socket
            self.socket.settimeout(0.5)
            self.stop = False
        def run(self):
            while not self.stop:
                try:
                    sys.stdout.write(self.socket.recv(1024))
                    sys.stdout.flush()
                except:
                    pass
        def kill(self):
            self.stop = True


class TimeoutException(Exception): 
    pass

    
