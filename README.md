nexpect.py
=======

Network Expect Python Module

This is a python module that acts much like pexpect but works with sockets over a network. It is useful for building network application clients.

The main functionality works by calling the n.expect() function with a regular expression as the argument. This will start listening for data on a socket until it matches the regular expression.

The examples show both a server use and a client use in a simple, illustrative scenario. Check it out for yourself!
