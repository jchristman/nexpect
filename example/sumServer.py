import nexpect, socket, thread, time, random

# This is the server handler. It takes a socket object and a connection information tuple as arguments
# and uses nexpect to control the flow of the program. It creates an nexpect object using the socket
# as the argument and then uses various methods to send data back and forth across the socket.
def handle(sock, conninfo):
    n = nexpect.spawn(sock)

    try:
        n.sendline('Welcome to the sum solver! We will send you a random length list of integers and you need to sum the list and send back the answer. The list will be formatted as START,1,2,3,END. You must send the answer back fast or else you will lose.')
        n.sendline()

        for i in xrange(1,101):
            listLength = (i + 3) * 2 + random.randint(0,i)  # Calculate a length for the list
            toSolve = []                                    # Create the list
            for j in xrange(listLength):                    # Iterate through the length and append a number between -i and i
                toSolve.append(random.randint(-i, i))
            ans = sum(x for x in toSolve)                   # Calculate the answer

            n.sendline('START,' + ''.join(str(x) + ',' for x in toSolve) + 'END')   # Send the list to the client
            try:
                data = n.expect(('\n', '\r\n'), timeout=2, incl=False)[0]   # Wait for the answer (followed by a '\n' or a '\r\n') but we don't care which regex we match
            except nexpect.TimeoutException as e:
                n.sendline('Timed out! Play faster!!!') # If it times out, we cut off the connection
                n.shutdown()                            # and gracefully close the socket and object
                return
            if int(data) == ans:
                n.sendline('Correct! Here\'s another.') # They got it correct
                continue
            else:
                n.sendline('Wrong! Got ' + data + ' but expected ' + str(ans))  # They got it wrong! Shutdown the socket
                n.shutdown()
                return
        n.sendline('You have solved all of my challenges! FLAG_0123456789') # They solved all of the challenges! Give them the flag.
        n.shutdown()
        print str(conninfo) + ' solved all of the challenges'
    except:
        n.shutdown()    # Something bad happened - shutdown!
        return

s = socket.socket()         # Create the socket server
s.bind(('localhost', 9000)) # Bind to the port
s.listen(1)                 # and listen!
while True:
    try:
        sock, conninfo = s.accept()                         # Accept connections
        thread.start_new_thread(handle, (sock, conninfo))   # And spawn a thread for their connection!
    except KeyboardInterrupt:
        exit()
    except:
        pass
