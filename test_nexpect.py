import unittest, thread, socket, nexpect, sys, time, ssl

class nexpectTest(unittest.TestCase):

    def startTestServer(self, port, withSSL=False):
        try:
            server = socket.socket()
            if withSSL:
                server = ssl.wrap_socket(server, server_side=True, certfile='test.crt', keyfile='test.key')
            server.bind(('0.0.0.0',port))
            server.listen(1)
            while True:
                sock,addr = server.accept()
                thread.start_new_thread(self.handler,(sock,))
        except:
            pass

    def handler(self, sock):
        try:
            data = ''
            while True:
                data = sock.recv(1024)
                if 'exit' in data:
                    return
                elif 'test_single_expect' in data:
                    sock.sendall('This is only a test.\n\n BOB')
                elif 'test_multi_expect' in data:
                    sock.sendall('This is only a test.\n\n Steve')
                elif 'Timeout' in data:
                    time.sleep(2)
                elif 'bad_regex' in data:
                    sock.sendall('Data that does not match regex')
                elif 'SSL_TEST' in data:
                    sock.sendall('This is in response to the SSL request and should be encrypted')
        except:
            return

    def setUp(self):
        thread.start_new_thread(self.startTestServer,(9000,False))
        thread.start_new_thread(self.startTestServer,(9001,True))
        time.sleep(1)

    def test_createModuleWithSocket(self):
        time.sleep(1) # Make sure the server has had time to set up

        sock = socket.socket()
        sock.connect(('localhost',9000))
        s = nexpect.nexpect(sock)
        self.assertEqual(s.timeout, 30)
        s.sendline('exit')
        s.shutdown()
        
        s = nexpect.spawn(('localhost',9000))
        self.assertEqual(s.timeout, 30)
        s.sendline('exit')
        s.shutdown()
        
        self.assertRaises(TypeError, nexpect.spawn, ('123'))

    def test_expect(self):
        s = nexpect.spawn(('localhost',9000))
        s.sendline('test_single_expect')
        returned = s.expect('B.B')
        shouldMatch = 'This is only a test.\n\n BOB'
        self.assertEqual(returned, shouldMatch)
        
        s.sendline('test_multi_expect')
        returned,index = s.expect(['B.B','Steve'])
        shouldMatch = ('This is only a test.\n\n Steve',1)
        self.assertEqual(shouldMatch[0], returned)
        self.assertEqual(shouldMatch[1], index)
        
        s.sendline('Timeout')
        with self.assertRaises(nexpect.TimeoutException):
            s.expect('timeout',timeout=1)

        s.sendline('bad_regex')
        with self.assertRaises(nexpect.TimeoutException):
            s.expect('BOB',timeout=1)    # Because we are expecting BOB and it will not be coming

        s.sendline('exit')
        s.shutdown()

    def test_SSL(self):
        s = nexpect.spawn(('localhost', 9001), withSSL=True)
        s.sendline('SSL_TEST')
        data = s.expect('encrypted')
        shouldMatch = 'This is in response to the SSL request and should be encrypted'
        self.assertEqual(shouldMatch, data)
        
        s.sendline('exit')
        s.shutdown()

if __name__ == '__main__':
    sys.argv.append('-v')
    unittest.main()
