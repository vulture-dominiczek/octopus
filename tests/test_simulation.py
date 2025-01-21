

from simulation import Step


def test_step_printing():

    step = Step(
        global_state = {
            'shared': {
                'a': 1,
                'b': 2
            },
            'process-1': {
                'a': 3,
                'b': 4
            },
            'process-2': {
                'a': 5,
                'b': 6
            }
        },
        per_process_operations = {
            'process-1': 'read',
            'process-2': 'write'
        },
        tick = 1
    )


    assert str(step) == '| 1     | read                                                         | {"a": 3, "b": 4}                         | write                                                        | {"a": 5, "b": 6}                         | {"a": 1, "b": 2}                                             |'