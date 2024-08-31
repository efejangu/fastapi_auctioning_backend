
class Node:
    def __init__(self, data:float):
        self.data = data
        self.next = None

class Stack:
    def __init__(self):
        self.head = None
        self.size = 0

    def peek (self):
        return self.head.data

    def push (self, data):
        new_node = Node(data)
        if self.size == 0:
            self.head = new_node
            self.size += 1
        new_node.next = self.head
        self.head = new_node
        self.size += 1

    def pop (self):
        if self.size == 0:
            return None
        data = self.head.data
        self.head = self.head.next
        self.size -= 1
        return data

    def collapse(self):
        while self.size > 0:
            self.pop()


