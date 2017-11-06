#!/usr/bin/env python3
"""
    Chord.py - Implementation of MIT's Chord Distributed Hash Table (DHT)
    Author:
        - Nidesh Chitrakar (nideshchitrakar@bennington.edu)
        - Hoanh An (hoanhan@bennington.edu)
    Date: 10/29/2017
"""

m = 3   # KEY_SPACE_SIZE (max 64)

class Node():
    def __init__(self, IP_ADDRESS, PORT, ID):
        self.IP_ADDRESS = IP_ADDRESS
        self.PORT = PORT
        self.ID = ID

    def to_dict(self):
        return 'ID: {0}, IP: {1}, PORT: {2}'.format(self.ID, self.IP, self.PORT)

class ChordInstance(object):
    def __init__(self, IP_ADDRESS, PORT, ID):
        self.IP_ADDRESS = IP_ADDRESS
        self.PORT = PORT
        self.NODE = Node(IP_ADDRESS, PORT, ID)
        self.ID = ID
        self.finger_table = self.create_finger_table()
        self.successor = self.finger_table[0]['successor'] #self.NODE
        self.predecessor = self

    def create_finger_table(self):
        finger_table = []
        for i in range(0,m):
            finger_table.append({})
            finger_table[i]['start'] = self.NODE.ID + (2**i)
        for i in range(0,m):
            finger_table[i]['range_start'] = finger_table[i]['start']
            if (i != m - 1):
                finger_table[i]['range_end'] = finger_table[i+1]['start']
            else:
                finger_table[i]['range_end'] = self.NODE.ID
            finger_table[i]['successor'] = self
        return finger_table

    def print_finger_table(self):
        print('Node {0} Successor: {1}, Predecessor {2}'.format(self.ID, self.successor.ID, self.predecessor.ID))
        for i in range (0,m):
            print("| {0} | [{1}, {2}) | {3} |".format(self.finger_table[i]['start'], self.finger_table[i]['range_start'],self.finger_table[i]['range_end'], self.finger_table[i]['successor'].ID))


    def is_between(self, value, start, end, including_start=False, including_end=False):
        """
        Check if value is in the range.
        :param value: Target value
        :param start: Start value
        :param end: End value
        :param including_start: Bool
        :param including_end: Bool
        :return: True if value is in the range.
        """
        print('Node{0}.is_between(val={1},start={2},end={3},include_start={4},include_end={5})'.format(self.ID,value,start,end,including_start,including_end))
        if not including_start and not including_end:
            if (start < value < end):
                return True
            elif (start > end) and (start < value <= (2**m - 1) or 0 <= value < end):
                return True
            return False
        elif not including_start and including_end:
            if (start == end):
                return True
            elif (start < value <= end):
                return True
            elif (start > end) and ((start < value <= (2**m - 1)) or (0 <= value <= end)):
                return True
            return False
        elif including_start and not including_end:
            if (start <= value < end):
                return True
            elif (start > end) and (start <= value <= (2**m - 1) or 0 <= value < end):
                return True
            elif (start == end):
                return True
            return False
        else:
            if (start <= value <= end):
                return True
            elif (start > end) and (start <= value <= (2**m - 1) or 0 <= value <= end):
                return True
            elif (start == end):
                return True
            return False

    def find_successor(self, ID):
        print('Node{0}.find_successor({1})'.format(self.ID, ID))
        n0 = self.find_predecessor(ID)
        print('-> Successor: {0}'.format(n0.successor.ID))
        return n0.successor

    def find_predecessor(self,ID):
        print('Node{0}.find_predecessor({1})'.format(self.ID, ID))
        n0 = self
        while not self.is_between(ID, n0.ID, n0.successor.ID, including_end=True):
            n0 = n0.closest_preceding_node(ID)
        print('-> Predecessor: {0}'.format(n0.ID))
        return n0

    def closest_preceding_node(self, ID):
        for i in range(m-1, 0, -1):    # from i = m down to 1
            if self.is_between(self.finger_table[i]['successor'].ID, self.ID, ID):
                return self.finger_table[i]['successor']
        return self

    def join(self, NODE):
        print('Node{0}.join({1})'.format(self.ID, NODE.ID))
        if (NODE.ID != None):
            self.init_finger_table(NODE)
            # self.update_others()
        else:
            for i in range(0,m):
                self.finger_table[i]['successor'] = self
            self.predecessor = self

    def init_finger_table(self, NODE):
        print('Node{0}.init_finger_table({1})'.format(self.ID, NODE.ID))

        self.finger_table[0]['successor'] = NODE.find_successor(self.finger_table[0]['start'])
        print('-> Updated Node {0} Finger Table[0][\'successor\'] to {1}'.format(self.ID, self.finger_table[0]['successor'].ID))

        self.predecessor = self.finger_table[0]['successor'].predecessor
        print('-> Set predecessor of Node {0} to {1}'.format(self.ID, self.predecessor.ID))

        self.finger_table[0]['successor'].predecessor = self
        print('-> Set predecessor of Node {1} to {0}'.format(self.ID, self.finger_table[0]['successor'].ID))

        print("-> Begin update every entry of Node {0} Finger Table".format(self.ID))
        # Start from 1 because already updated entry 0
        for i in range(1,m):
            self.print_finger_table()
            if self.is_between(self.finger_table[i]['start'], self.ID, self.finger_table[i-1]['successor'].ID, including_start=True):
                print('Value {0} is in [{1},{2})'.format(self.finger_table[i]['start'], self.ID, self.finger_table[i]['successor'].ID))
                self.finger_table[i]['successor'] = self.finger_table[i-1]['successor']
                print('-> Updated Node {1} Finger Table[{0}][\'successor\'] to {2}'.format(i, self.ID, self.finger_table[i-1]['successor'].ID))
            else:
                print('Value {0} is NOT in [{1},{2})'.format(self.finger_table[i]['start'],self.ID,self.finger_table[i]['successor'].ID))
                self.finger_table[i]['successor'] = NODE.find_successor(self.finger_table[i]['start'])
                print('-> Updated Node {1} Finger Table[{0}][\'successor\'] to {2}'.format(i, self.ID, NODE.find_successor(self.finger_table[i-1]['start'])))
        self.print_finger_table()

    def update_others(self):
        print('Node{0}.update_others(): update finger_table of other nodes'.format(self.ID))
        for i in range(0,m):
            val = self.reverse_count(self.ID - 2**(i))
            #print(val)
            p = self.find_predecessor(self.reverse_count(self.ID - 2**i))
            print('Predecessor of {0} is {1}'.format(val, p.ID))
            p.update_finger_table(self, i)

    def reverse_count(self, value):
        temp = 0
        if value < 0:
            temp = 2**m - value
        else:
            temp = value
        return temp

    def update_finger_table(self, NODE, i):
        print('Node{0}.update_finger_table({1}, {2})'.format(self.ID, NODE.ID, i))
        if self.is_between(NODE.ID,self.ID, self.finger_table[i]['successor'].ID, including_start=True):
            self.finger_table[i]['successor'] = NODE
            p = self.predecessor
            p.update_finger_table(NODE, i)
            self.print_finger_table()


if __name__ == '__main__':
    chord1 = ChordInstance('0.0.0.0', 9000, 1)
    chord2 = ChordInstance('127.0.0.1', 9001, 3)

    print("-> BEFORE JOIN")

    chord1.print_finger_table()
    chord2.print_finger_table()
    chord2.join(chord1)

    print("-> AFTER JOIN")

    chord1.print_finger_table()
    chord2.print_finger_table()

    # print(chord1.is_between(7,6,1))
    # print(chord1.is_between(0,6,1,including_start=True))
    # print(chord1.is_between(5,6,1,including_start=True))
    # print(chord1.is_between(3,3,7,including_start=True, including_end=True))
    # print(chord1.is_between(3,4,2,including_start=True))
