#!/usr/bin/env python3

"""
    node.py - A Node Class
    Author:
        - Nidesh Chitrakar (nideshchitrakar@bennington.edu)
        - Hoanh An (hoanhan@bennington.edu)
    Date: 10/30/2017
"""

from utils import *

class Node():
    """
    Model for a Node. Each instance holds values of IP Address, Port, and ID
    generated by a hash function.
    """
    def __init__(self, IP_ADDRESS, PORT):
        """
        Initialize a Node.
        :param IP_ADDRESS: String
        :param PORT: Int
        :param ID: Int
        """
        self.IP_ADDRESS = IP_ADDRESS
        self.PORT = PORT
        self.ID = chord_hash("{0}:{1}".format(IP_ADDRESS, PORT))

    def to_dict(self):
        """
        Print information of a Node.
        :return: String
        """
        return 'ID: {0}, IP: {1}, PORT: {2}'.format(self.ID, self.IP_ADDRESS, self.PORT)
