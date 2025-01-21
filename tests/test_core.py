
from core import read, prepare_write, can_lock, power_set
from core import ReadOperation, WriteOperation, DataTransfer, Process, Assignment, LetOperation, ComputeOperation, Lock


def test_read():

    shared_state = {
        'data': [
            {
                'a': 1,
                'b': 2
            }
        ]
    }

    assert read(shared_state, 'data.0.a') == 1


def test_prepare_write():
    
    shared_state = {
        'data': [
            {
                'a': 1,
                'b': 2
            }
        ]
    }

    it, key = prepare_write(shared_state, 'data.0.a')
    it[key] = 3

    assert shared_state['data'][0]['a'] == 3



def test_read_operation():
    
    shared_state = {
        'data': {
            'a': 1,
            'b': 2
        }
    }

    process = Process('process-1')
    process.local_state = {}
    process.shared_state = shared_state

    data_transfer = [
        DataTransfer(from_path='data.a', to_path='a'),
        DataTransfer(from_path='data.b', to_path='b')
    ]

    read_operation = ReadOperation(process, data_transfer)
    read_operation()

    assert process.local_state['a'] == 1
    assert process.local_state['b'] == 2


def test_write_operation():
    
    shared_state = {
        'data': {
        }
    }

    process = Process('process-1')
    process.local_state = {
        'a': 1,
        'b': 2
    }
    process.shared_state = shared_state

    data_transfer = [
        DataTransfer(from_path='a', to_path='data.a'),
        DataTransfer(from_path='b', to_path='data.b')
    ]

    write_operation = WriteOperation(process, data_transfer)
    write_operation()

    assert shared_state['data']['a'] == 1
    assert shared_state['data']['b'] == 2


def test_let_operation():
    

    process = Process('process-1')

    assignments = [
        Assignment(path = 'a', value = 1),
        Assignment(path = 'b', value = 2)
    ]

    let_operation = LetOperation(process, assignments)
    let_operation()

    assert process.local_state['a'] == 1
    assert process.local_state['b'] == 2


def test_compute_operation():
    

    process = Process('process-1')
    process.local_state = {
        'a': 1,
        'b': 2
    }

    def add(state):
        state['c'] = state['a'] + state['b']

    compute_operation = ComputeOperation(process, add)
    compute_operation()

    assert process.local_state['c'] == 3


def test_can_lock():

    l1 = Lock(data_path = 'data.a')
    l2 = Lock(data_path = 'data.a.b')

    locks = [l1]

    # l2 is more specific than l1
    assert can_lock(locks, l2) == False

    locks = [l2]
    assert can_lock(locks, l1) == True

def test_power_set():

    lst = [1, 2, 3]

    result = power_set(lst)

    assert result == [[1], [2], [3], [1, 2], [1, 3], [2, 3], [1, 2, 3]]

