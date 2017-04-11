import os
import socket
import subprocess
import datetime
import sqlite3


def blacklist_ip(ip_address):
    """Method to blacklist ip address."""
    try:
        if socket.inet_aton(ip_address):
            command = "ipset add blacklist {}".format(ip_address)
            subprocess.call(command.split())
    except Exception as err:
        print(err)


def blacklist_ips(connection_handler=None):
    try:
        cursor = connection_handler.execute("select * from whitelist")
        for row in cursor:
            whitelist_datetime = datetime.datetime.fromtimestamp(float(row[1]))
            minutes = (datetime.datetime.now() - whitelist_datetime).seconds / 60
            print minutes
            if minutes >= 2:
                blacklist_ip(row[0])
                connection_handler.execute("delete from whitelist where ip='{}'".format(row[0]))
                connection_handler.commit()
    except Exception as err:
        print(err)


def main():
    try:
        conn = sqlite3.connect("/home/pi/corseco_captive_portal/components/socket_client.db")
        blacklist_ips(conn)

    except Exception as err:
        print(err)


if __name__ == "__main__":
    main()
