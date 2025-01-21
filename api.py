
import copy, json
from core import Process, DataTransfer
from simulation import ConcurrencySolver
from config import PrintOpts


def dict_subsumes(superset, subset):

    for key, value in subset.items():
        if key not in superset:
            return False
        if isinstance(value, dict):
            if not isinstance(superset[key], dict):
                return False
            if not dict_subsumes(superset[key], value):
                return False
        else:
            if superset[key] != value:
                return False
    return True


def verifiy_validity(shared_state, should_be):
    return dict_subsumes(shared_state, should_be)


class Octo:

    shared_state = {}

    locks = [] 

    processes = []
    
    @staticmethod
    def init_shared_state(shared_state):
        Octo.shared_state = shared_state

    @staticmethod
    def process(**kwargs):
        process = Process(kwargs['name'])
        Octo.processes.append(process)
        return process
    
    @staticmethod
    def solve_exact(**kwargs):

        processes = copy.deepcopy(Octo.processes)
        shared_state = copy.deepcopy(Octo.shared_state)
        locks = copy.deepcopy(Octo.locks)

        for p in processes:
            p.shared_state = shared_state
            p.locks = locks

        solver = ConcurrencySolver(processes = processes, 
                                   shared_state = shared_state, 
                                   locks = locks)
        
        path = solver.solve_exact()

        output_path = kwargs['output']

        with open(output_path, 'w') as f:
            run_name = 'Run #1'
            if 'run_name' in kwargs:
                run_name = kwargs['run_name']

            f.write(f'{run_name}\n\n')


            s = ''
            s += f'| {'TICK':<{PrintOpts.TICK_WIDTH}} |'

            for p in processes:
                s += f' {p.name+' OPERATION':<{PrintOpts.OPERATION_WIDTH}} |'
                if PrintOpts.PRINT_LOCALS:
                    s += f' {p.name+' LOCALS':<{PrintOpts.LOCAL_STATE_WIDTH}} |'

            s += f' {' SHARED':<{PrintOpts.SHARED_STATE_WIDTH}} |\n'

            f.write(s)

            for step in path:
                f.write(str(step)+'\n')

            last_state = path[-1].global_state['shared']

            if 'validity_check' in kwargs:
                check = verifiy_validity(last_state, kwargs['validity_check'])

                f.write('\n')

                f.write(f'Validity condition: {json.dumps(kwargs['validity_check'])}\n')
                status = 'SUCCESS' if check else 'FAILURE'
                f.write(f'Status: {status}\n')

    @staticmethod
    def solve_lattice(**kwargs):

        processes = copy.deepcopy(Octo.processes)
        shared_state = copy.deepcopy(Octo.shared_state)
        locks = copy.deepcopy(Octo.locks)

        for p in processes:
            p.shared_state = shared_state
            p.locks = locks

        solver = ConcurrencySolver(processes = processes, 
                                   shared_state = shared_state, 
                                   locks = locks)
        
        paths = solver.solve_lattice()

        output_path = kwargs['output']

        with open(output_path, 'w') as f:
            body = ''
            statuses = []

            for i, path in enumerate(paths):
                body += f'Run #{i+1}\n\n'

                s = ''
                s += f'| {'TICK':<{PrintOpts.TICK_WIDTH}} |'

                for p in processes:
                    s += f' {p.name+' OPERATION':<{PrintOpts.OPERATION_WIDTH}} |'
                    if PrintOpts.PRINT_LOCALS:
                        s += f' {p.name+' LOCALS':<{PrintOpts.LOCAL_STATE_WIDTH}} |'

                s += f' {' SHARED':<{PrintOpts.SHARED_STATE_WIDTH}} |\n'

                body += s

                for step in path:
                    body += str(step)+'\n'

                last_state = path[-1].global_state['shared']

                if 'validity_check' in kwargs:
                    check = verifiy_validity(last_state, kwargs['validity_check'])

                    body += '\n'

                    body += f'Validity condition: {json.dumps(kwargs['validity_check'])}\n'
                    status = 'SUCCESS' if check else 'FAILURE'
                    body += f'Status: {status}\n'
                    statuses.append(status)
            
            total = len(statuses) 
            success = statuses.count('SUCCESS')
            failure = statuses.count('FAILURE')

            f.write(f'Successful runs: {success}/{total}\n')
            f.write(f'Failed runs: {failure}/{total}\n-----------------\n\n')

            for i in range(total):
                f.write(f'Run #{i+1}: {statuses[i]}\n')

            f.write('-----------------\n\n')
            f.write(body)



