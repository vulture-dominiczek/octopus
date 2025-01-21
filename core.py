
from itertools import chain, combinations


class DataTransfer:

    def __init__(self, **kwargs):
        if not 'from_path' in kwargs or not 'to_path' in kwargs:
            raise ValueError('DataTransfer requires from_path and to_path')
        self.from_path = kwargs['from_path']
        self.to_path = kwargs['to_path']

    def __str__(self):
        return f'{self.from_path} -> {self.to_path}'



class Assignment:

    def __init__(self, **kwargs):
        if not 'path' in kwargs or not 'value' in kwargs:
            raise ValueError('Assignment requires path and value')
        self.path = kwargs['path']
        self.value = kwargs['value']

    def __str__(self):
        return f'{self.path} := {self.value}'
    

class Lock:

    def __init__(self, **kwargs):
        if not 'data_path' in kwargs:
            raise ValueError('Lock requires data_path')
        self.data_path = kwargs['data_path']
        self.process = kwargs.get('process', None)

    def __str__(self):
        return f'{self.data_path}'



def read(store, from_path):

    components = from_path.split('.')

    it = store
    for component in components:
        try:
            idx = int(component)
        except ValueError:
            idx = component
        it = it[idx]
    
    return it

def prepare_write(store, to_path):

    components = to_path.split('.')

    it = store
    for component in components[:-1]:
        try:
            idx = int(component)
        except ValueError:
            idx = component
        it = it[idx]

    return it, components[-1]


def can_lock(locks, lock):
    for l in locks:
        # is lock more specific
        if lock.data_path.startswith(l.data_path):
            return False
    return True

def power_set(lst):
    all_sets = chain.from_iterable(combinations(lst, r) for r in range(1, len(lst) + 1))
    return [list(subset) for subset in all_sets]



class ReadOperation:


    def __init__(self, process, data_transfer):
        self.process = process
        self.data_transfer = data_transfer

    def __call__(self, shared_state, locks):
        for dt in self.data_transfer:
            it, key = prepare_write(self.process.local_state, dt.to_path)
            it[key] = read(shared_state, dt.from_path)

    def __str__(self):
        return f'Read {", ".join([str(dt) for dt in self.data_transfer])}'
    
    def __repr__(self):
        return self.__str__()
       
class WriteOperation:


    def __init__(self, process, data_transfer):
        self.process = process
        self.data_transfer = data_transfer

    def __call__(self, shared_state, locks):
        for dt in self.data_transfer:
            it, key = prepare_write(shared_state, dt.to_path)
            it[key] = read(self.process.local_state, dt.from_path)

    def __str__(self):
        return f'Write {", ".join([str(dt) for dt in self.data_transfer])}'
    
    def __repr__(self):
        return self.__str__()

class LetOperation:

    def __init__(self, process, assignments):
        self.process = process
        self.assignments = assignments

    def __call__(self, shared_state, locks):
        for assignment in self.assignments:
            it, key = prepare_write(self.process.local_state, assignment.path)
            it[key] = assignment.value

    def __str__(self):
        return f'Let {", ".join([str(a) for a in self.assignments])}'
    
    def __repr__(self):
        return self.__str__()


class ComputeOperation:

    def __init__(self, process, fn, description = ''):
        self.process = process
        self.fn = fn
        self.description = description

    def __call__(self, shared_state, locks):
        self.fn(self.process.local_state)

    def __str__(self):
        return f'Compute {self.description}'
    
    def __repr__(self):
        return self.__str__()


class LockOperation:

    def __init__(self, process, data_path):
        self.process = process
        self.data_path = data_path
        self.lock = Lock(data_path = self.data_path, process = self.process)

    def __call__(self, shared_state, locks):
        if can_lock(locks, self.lock): 
            locks.append(self.lock)
            return True
        else:
            return False

    def __str__(self):
        return f'Lock {self.data_path}'

    def __repr__(self):
        return self.__str__()


class UnlockOperation:
    
    def __init__(self, process, data_path):
        self.process = process
        self.data_path = data_path

    def __call__(self, shared_state, locks):
        try:
            index = next((i for i, l in enumerate(locks) if l.data_path == self.data_path), None)
            locks.pop(index)
        except TypeError:
            pass

    def __str__(self):
        return f'Unlock {self.data_path}'
    
    def __repr__(self):
        return self.__str__()


class NoopOperation:
    
    def __init__(self):
        pass

    def __call__(self, shared_state, locks):
        pass

    def __str__(self):
        return 'Noop'


class Process:

    def __init__(self, name):
        self.name = name
        self.local_state = {}
        self.operations = []
        self.is_blocked = False

    def read(self, data_transfers):
        self.operations.append(ReadOperation(self, data_transfers))

    def write(self, data_transfers):
        self.operations.append(WriteOperation(self, data_transfers))

    def let(self, assignments):
        self.operations.append(LetOperation(self, assignments))

    def noop(self):
        self.operations.append(NoopOperation())

    def compute(self, fn, description = ''):
        self.operations.append(ComputeOperation(self, fn, description=description))

    def lock(self, data_path):
        self.operations.append(LockOperation(self, data_path))

    def unlock(self, data_path):
        self.operations.append(UnlockOperation(self, data_path))    



