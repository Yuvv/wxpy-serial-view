# -*- coding: utf-8 -*-

# @File   : tcp.py
# @Author : Yuvv
# @Date   : 2018/7/21

import logging
import socket
import socketserver
import threading


class ThreadedTCPRequestHandler(socketserver.StreamRequestHandler):

    def handle(self):
        data = str(self.request.recv(1024), 'ascii')
        cur_thread = threading.current_thread()
        response = bytes("{}: {}".format(cur_thread.name, data), 'ascii')
        self.request.sendall(response)


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


class TCPServerThread(threading.Thread):

    def __init__(self, host, port, request_size, client_accept_handler):
        super(TCPServerThread, self).__init__(daemon=True)
        self.alive = True
        self._lock = threading.Lock()
        self.tcp_server = socket.socket(socket.AF_INET,
                                        socket.SOCK_STREAM)
        self.tcp_server.bind((host, port))
        self.tcp_server.listen(request_size)
        self.client_accept_handler = client_accept_handler

    def stop(self):
        """Stop the reader thread"""
        self.alive = False
        if hasattr(self.tcp_server, 'cancel_read'):
            self.tcp_server.shutdown(socket.SHUT_RDWR)
        self.join(2)

    def run(self):
        while self.alive:
            sock, addr = self.tcp_server.accept()
            t = threading.Thread(target=self.client_accept_handler,
                                 args=(sock, addr),
                                 daemon=True)
            t.start()

    def close(self):
        """Close the serial port and exit reader thread (uses lock)"""
        # use the lock to let other threads finish writing
        with self._lock:
            # first stop reading, so that closing can be done on idle port
            self.stop()
            self.tcp_server.shutdown(socket.SHUT_RDWR)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Leave context: close port"""
        self.close()


def start_tcp_server(host, port, max_requests, client_handler):
    tcp_server = socket.socket(socket.AF_INET,
                               socket.SOCK_STREAM)
    tcp_server.bind((host, port))
    tcp_server.listen(max_requests)
    while True:
        sock, addr = tcp_server.accept()
        logging.info('Accept new connection from %s...', addr)
        client_handler(sock)


def start_a_tcp_listener(host, port, max_requests, client_handler):
    t = threading.Thread(target=start_tcp_server,
                         args=(host, port, max_requests, client_handler),
                         daemon=True)
    t.start()
