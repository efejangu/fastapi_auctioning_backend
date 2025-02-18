
class Node:
    def __init__(self, data:dict):
        self.data = data
        self.next = None

class Stack:
    def __init__(self):
        self.head = None
        self._size = 0

    def peek (self) -> None | dict:
        """Returns the top element in the stack without removing it.
        If the stack is empty, it returns None.
        """
        if self.head is None:
            return None
        return self.head.data
        
  
    def push(self, data: dict):
        if not isinstance(data, dict) or 'bid' not in data or 'bidder' not in data:
            raise ValueError("Data must be a dictionary with 'bid' and 'bidder' keys")
        new_node = Node(data)
        if self.get_size() == 0:
            self.head = new_node
        else:
            new_node.next = self.head
            self.head = new_node
        self._size += 1
        return self._size

    def pop (self):
        if self._size() == 0:
            return None
        data = self.head.data
        self.head = self.head.next
        self._size -= 1
        return data

    def collapse(self):
        while self.head is not None:
            current = self.head
            self.head = self.head.next
            del current
        self._size = 0


    def get_size(self):
        return self._size

