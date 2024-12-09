import ipaddress
from datetime import datetime
import socket
import random
import logging
import json
import sqlite3
from cryptography.fernet import Fernet


TIMINGS: list = [10, 1440, 5760, 10080, 20160, 40320, (40320*6)]
BTN1_IMAGE = "./Images/BTN1.png"
BTN2_IMAGE = "./Images/BTN2.png"
SMLBTN1_IMAGE = "./Images/SMLBTN1.png"
SMLBTN2_IMAGE = "./Images/SMLBTN2.png"
SMLBTN3_IMAGE = "./Images/SMLBTN3.png"
SMLBTN4_IMAGE = "./Images/SMLBTN4.png"
SMLBTN5_IMAGE = "./Images/SMLBTN5.png"
BG_IMAGE = "./Images/BCKGRND.png"
SQR_IMAGE = "./Images/SQR.png"
SERVER_HOST: str = "0.0.0.0"
CLIENT_HOST: str = "127.0.0.1"
PORT: int = 12345
BUFFER_SIZE: int = 1024
HEADER_LEN: int = 2
FORMAT: str = 'utf-8'
DISCONNECT_MSG: str = "EXIT"

# prepare Log file
LOG_FILE = 'LOG.log'
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def check_cmd(data) -> bool:
    """Check if the command is defined in the protocol"""
    print(data)
    data = data.upper()
    listdata = data.split(">")
    return listdata[0] in ("TIME", "RAND", "NAME", "REG", "LOG", DISCONNECT_MSG)


def create_request_msg(data) -> str:
    """Create a valid protocol message, will be sent by client, with length field"""
    request = ''
    if check_cmd(data):
        request += f"{len(data):02d}{data}"
    else:
        request = f"{len('Non-supported cmd')}Non-supported cmd"
    return request


def create_response_msg(data) -> str:
    """Create a valid protocol message, will be sent by server, with length field"""
    response = "Non-supported cmd"
    list = data.split(">")
    if list[0] == DISCONNECT_MSG:
        response = "Exit request accepted"
    elif list[0] == "REG":
        json_acceptable_string = list[1].replace("'", "\"")
        data = json.loads(json_acceptable_string)
        write_to_log("data in creating:" + json_acceptable_string)
        return data, 1
    elif list[0] == "LOG":
        json_acceptable_string = list[1].replace("'", "\"")
        data = json.loads(json_acceptable_string)
        response, table = login(data) #table 2 if singed successfully, 0 if wrong account details
        return response, table
    elif list[0] == "TIME":
        response = str(datetime.now())
    elif list[0] == "NAME":
        response = socket.gethostname()
    elif list[0] == "RAND":
        response = f"{random.randint(1,1000)}"
    elif list[0] == DISCONNECT_MSG:
        response = "Exit request accepted"
    response = f"{len(response):02d}{response}"
    return response, 0

def register(data: json):
    login = data["login"]
    password = data["password"]
    connection = sqlite3.connect("RememberDB.db")
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS Users 
    (id INTEGER PRIMARY KEY,
    login TEXT NOT NULL,
    password TEXT NOT NULL,
    key TEXT NOT NULL)''')
    key = Fernet.generate_key()
    encryption = Fernet(key)
    cursor.execute(
        """INSERT INTO Users (login, password, key) VALUES(?, ?, ?);""",
(

                login,
                encryption.encrypt(password.encode()),
                key)
            )
    return "registration succeed"
def login(data: json):
    log = data["login"]
    password = data["password"]
    connection = sqlite3.connect("Users.db")
    cursor = connection.cursor()
    cursor.execute("SELECT login, password FROM Users ")
    if cursor.fetchall():
        if log in cursor.fetchall()[0] and password in cursor.fetchall()[1]:
            for row in cursor.fetchall():
                if row[0] == log and row[1] == password:
                    return "signing in...", 2
            response = "wrong password"
            response = f"{len(response):02d}{response}"
            return response, 0
        elif log in cursor.fetchall()[0] and not(password in cursor.fetchall()[1]):
            response = "wrong password"
            response = f"{len(response):02d}{response}"
            return response, 0
        else:

            response = "the user does not exist"
            response = f"{len(response):02d}{response}"
            return response, 0

    else:
        response = "the user does not exist"
        response = f"{len(response):02d}{response}"
        return response, 0


def receive_msg(my_socket: socket) -> (bool, str):
    """Extract message from protocol, without the length field
       If length field does not include a number, returns False, "Error" """
    str_header = my_socket.recv(HEADER_LEN).decode(FORMAT)
    length = int(str_header)
    if length > 0:
        buf = my_socket.recv(length).decode(FORMAT)
    else:
        return False, "Error"

    return True, buf


def write_to_log(msg):
    logging.info(msg)
    print(msg)
