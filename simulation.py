
import json
import copy

from config import PrintOpts

from core import LockOperation, can_lock, power_set


class Step:

    def __init__(self, **kwargs):
        self.global_state = kwargs['global_state']
        self.per_process_operations = kwargs['per_process_operations']
        self.process_names = kwargs['process_names']
        self.tick = kwargs['tick']

    def __str__(self):
        s = ''
        s += f'| {self.tick:<{PrintOpts.TICK_WIDTH}} |'

        for k in self.process_names:
            v = self.per_process_operations.get(k, '')
            s += f' {v:<{PrintOpts.OPERATION_WIDTH}} |'
            if PrintOpts.PRINT_LOCALS:
              d = json.dumps(self.global_state[k]) if self.global_state[k] else ''
              s += f' {d:<{PrintOpts.LOCAL_STATE_WIDTH}} |'

        s += f' {json.dumps(self.global_state["shared"]):<{PrintOpts.SHARED_STATE_WIDTH}} |'

        return s
    
    def __repr__(self):
        return json.dumps(self.per_process_operations)


class ConcurrencySolver:
    
    def __init__(self, **kwargs):
        self.processes = kwargs['processes']
        self.shared_state = kwargs['shared_state']
        self.locks  = kwargs['locks']
        self.paths = []


    def solve_exact(self):
        
        path = []

        tick = 1

        while True:
            step_operations = []
            for p in self.processes:
                try:
                    step_operations.append(p.operations.pop(0))
                except IndexError:
                    pass
           
            per_process_operations = {}

            executed_count = 0
            for op in step_operations:
                per_process_operations[op.process.name] = str(op)
                
                if isinstance(op, LockOperation):
                    if can_lock(self.locks, op.lock):
                        op()
                        executed_count += 1
                    else:
                        op.process.operations.insert(0, op)

                else:
                    op()
                    executed_count += 1

            if executed_count == 0:
                break

            global_state = {
                'shared': copy.deepcopy(self.shared_state)
            }

            for p in self.processes:
                global_state[p.name] = copy.deepcopy(p.local_state)

            path.append(Step(global_state = global_state, 
                             per_process_operations = per_process_operations, 
                             tick = tick,
                             process_names = [p.name for p in self.processes]))

            tick += 1

        return path
    
    
    def solve_lattice(self):
        
        self.paths = []

        self.solve_step(path = [], tick = 1)

        return self.paths
    
    def solve_step(self, path, tick):

        shared_state_backup = copy.deepcopy(self.processes[0].shared_state)
        locks_backup = copy.deepcopy(self.processes[0].locks)
        local_states_backup = {}
        for p in self.processes:
            local_states_backup[p.name] = copy.deepcopy(p.local_state)
        operations_backup = {}
        for p in self.processes:
            operations_backup[p.name] = copy.copy(p.operations)
        
        all_operations = []
        for p in self.processes:
            try:
                all_operations.append(p.operations[0])
            except IndexError:
                pass
            

        operation_sets = power_set(all_operations)
        operation_sets_filtered = []

        for op_set in operation_sets:
            dirty = False
            self.processes[0].locks = copy.deepcopy(locks_backup)
            for op in op_set:
                if isinstance(op, LockOperation) and can_lock(self.processes[0].locks, op.lock):
                    op()
                elif isinstance(op, LockOperation):
                    dirty = True
                    break
            if not dirty:
                operation_sets_filtered.append(op_set)
   
        
        
        for operations in operation_sets_filtered:

            for p in self.processes:
                p.shared_state = shared_state_backup
                p.local_state = copy.deepcopy(local_states_backup[p.name])
                p.operations = copy.copy(operations_backup[p.name])
                p.locks = locks_backup

            per_process_operations = {}

            for op in operations:
                per_process_operations[op.process.name] = str(op)
            
                if isinstance(op, LockOperation):
                    if can_lock(op.process.locks, op.lock):
                        op()
                        op.process.operations.pop(0)
                else:
                    op()
                    op.process.operations.pop(0)


            
            global_state = {
                'shared': copy.deepcopy(self.processes[0].shared_state)
            }

            for p in self.processes:
                global_state[p.name] = p.local_state


            new_path = copy.deepcopy(path)
            new_path.append(Step(global_state = global_state, 
                                 per_process_operations = per_process_operations, 
                                 tick = tick,
                                 process_names = [p.name for p in self.processes]))
            
            

            if all([len(p.operations) == 0 for p in self.processes]):
                if (new_path):
                    self.paths.append(new_path)
                return

            self.solve_step(path = new_path, tick = tick + 1)

