class SortedQueue:
    '''
    Basic iterable sorted queue
    '''
    def __init__(self, items=[]):
        self.items = items

    def append(self, item):
        self.items.append(item)
        self.items.sort()

    def pop(self, item):
        self.items.pop(item)
        self.items.sort()

    def __getitem__(self, i):
        return self.items[i]

    def __iter__(self):
        return self.items.__iter__()

    def __len__(self):
        return len(self.items)

