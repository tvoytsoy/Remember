import threading
from Protocol import *

# events
NEW_CONNECTION: int = 1
CLOSE_CONNECTION: int = 2
class CServerBL:

    def __init__(self, host, port):

        # Open the log file in write mode, which truncates the file to zero length
        with open(LOG_FILE, 'w'):
            pass  # This block is empty intentionally

        self._host = host
        self._port = port
        self._server_socket = None
        self._is_srv_running = True
        self._client_handlers = []

    def stop_server(self):
        try:
            self._is_srv_running = False
            # Close server socket
            if self._server_socket is not None:
                self._server_socket.close()
                self._server_socket = None

            if len(self._client_handlers) > 0:
                # Waiting to close all opened threads
                for client_thread in self._client_handlers:
                    client_thread.join()
                write_to_log(f"[SERVER_BL] All Client threads are closed")

        except Exception as e:
            write_to_log("[SERVER_BL] Exception in Stop_Server fn : {}".format(e))

    def start_server(self):
        try:
            self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._server_socket.bind((self._host, self._port))
            self._server_socket.listen(5)
            write_to_log(f"[SERVER_BL] listening...")

            while self._is_srv_running and self._server_socket is not None:

                # Accept socket request for connection
                client_socket, address = self._server_socket.accept()
                write_to_log(f"[SERVER_BL] Client connected {client_socket}{address} ")

                # Start Thread
                cl_handler = CClientHandler(client_socket, address, self.fire_event)
                cl_handler.start()
                self._client_handlers.append(cl_handler)
                write_to_log(f"[SERVER_BL] ACTIVE CONNECTION {threading.active_count() - 1}")

                self.fire_event(NEW_CONNECTION, cl_handler)
                write_to_log(f"[SERVER_BL] fire event - NEW CONNECTION")




        # ??? something happens here
        # except Exception as e:
        #    write_to_log("[SERVER_BL] Exception in start_server fn : {}".format(e))
        finally:
            write_to_log(f"[SERVER_BL] Server thread is DONE")

    def fire_event(self, enum_event: int, client_handle):
        pass

class CClientHandler(threading.Thread):

    def __init__(self, client_socket, address, fn):
        super().__init__()

        self.client_socket = client_socket
        self.address = address
        self.callback = fn

    def run(self):
        # This code run in separate thread for every client
        connected = True
        while connected:
            # 1. Get message from socket and check it
            valid_msg, msg = receive_msg(self.client_socket)
            if valid_msg:
                # 2. Save to log
                write_to_log(f"[SERVER_BL] received from {self.address}] - {msg}")
                # 3. If valid command - create response
                if check_cmd(msg):
                    # 4. Create response
                    response = create_response_msg(msg)
                    # 5. Save to log
                    write_to_log("[SERVER_BL] send - " + response)
                    # 6. Send response to the client
                    self.client_socket.send(response.encode(FORMAT))
                else:
                    # if received command not supported by protocol, just send it back "as is"
                    # 4. Create response
                    response = "Non-supported cmd"
                    response = f"{len(response):02d}{response}"
                    # 5. Save to log
                    write_to_log("[SERVER_BL] send - " + response)
                    # 6. Send response to the client
                    self.client_socket.send(response.encode(FORMAT))

                # Handle DISCONNECT command
                if msg == DISCONNECT_MSG:
                    connected = False

        self.client_socket.close()
        write_to_log(f"[SERVER_BL] Thread closed for : {self.address} ")

        self.callback(CLOSE_CONNECTION, self)
if __name__ == "__main__":
    server = CServerBL(SERVER_HOST, PORT)
    server.start_server()

