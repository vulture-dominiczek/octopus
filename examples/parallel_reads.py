
import os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from core import DataTransfer
from api import Octo
from config import PrintOpts

PrintOpts.PRINT_LOCALS = False

Octo.init_shared_state({ 'a': 1, 'b': 2 })

p1 = Octo.process(name = 'Alice')
p2  = Octo.process(name = 'Bob')



def incA(locals):
    locals['a'] += 1

p1.read([DataTransfer(from_path='a', to_path='a')])
p1.compute(incA, description='Increment a')
p1.write([DataTransfer(from_path='a', to_path='a')])

def incB(locals):
    locals['b'] += 1

p2.read([DataTransfer(from_path='b', to_path='b')])
p2.compute(incB, description='Increment b')
p2.write([DataTransfer(from_path='b', to_path='b')])

Octo.solve_exact(output='output.txt', validity_check={'a': 2, 'b': 3})