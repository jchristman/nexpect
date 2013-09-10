import nexpect

host = 'localhost'  # Define the host and port
port = 9000

n = nexpect.spawn((host, port)) # Create an nexpect object with the host, port tuple instead of a socket object
n.expect('lose.')   # Wait for the end of the intro before entering the game loop

while True:                         # We don't know how many puzzles we will need to solve so just keep solving until something different happens
    n.expect('START,', timeout=3)   # By setting a timeout, we will guarantee that we will print out any unexpected data that comes to us because it won't match out regex
    lst = n.expect(',END', incl=False).split(',')   # Get the list out of the socket
    ans = sum(int(x) for x in lst)  # Sum the list
    print 'Sending answer: ' + str(ans) # Print some fun data
    n.sendline(ans) # Send the answer and continue the loop
