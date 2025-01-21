
from api import verifiy_validity


def test_verifiy_validity():
    
    shared_state = {
        'data': {
            'a': 1,
            'b': 2
        }
    }

    should_be = {
        'data': {
            'a': 1,
            'b': 2
        }
    }

    assert verifiy_validity(shared_state, should_be) == True

    should_be = {
        'data': {
            'a': 1,
            'b': 3
        }
    }

    assert verifiy_validity(shared_state, should_be) == False

    should_be = {
        'data': {
            'a': 1
        }
    }

    assert verifiy_validity(shared_state, should_be) == True

    should_be = {
        'data': {
            'a': 1,
            'b': 2,
            'c': 3
        }
    }

    assert verifiy_validity(shared_state, should_be) == False