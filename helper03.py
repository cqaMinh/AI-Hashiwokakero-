import heapq
import time
import tracemalloc
from itertools import combinations, product
from pysat.solvers import Glucose4
from pysat.card import CardEnc, EncType
from hashiclass import HashiSolver

def _model_to_solution(self, model):
        """Chuyển đổi model từ PySAT thành định dạng assignment."""
        assignment = [0] * len(self.potential_bridges)
        rev_var_map = {v: k for k, v in self.var_map.items()}
        
        for lit in model:
            if lit > 0 and lit in rev_var_map:
                bridge_idx, count = rev_var_map[lit]
                if count == 2:
                    assignment[bridge_idx] = 2
                elif count == 1 and assignment[bridge_idx] == 0: 
                    assignment[bridge_idx] = 1
        return assignment

def solve_with_pysat(self):
        print("--- Giải bằng PySAT ---")
        start_time = time.time()
        tracemalloc.start()
        base_clauses = self._generate_cnf()
        
        with Glucose4(bootstrap_with=base_clauses) as solver:
            while solver.solve():
                model = solver.get_model()
                solution = self._model_to_solution(model)
                
                if self._is_connected(solution):
                    end_time = time.time()
                    current, peak = tracemalloc.get_traced_memory()
                    tracemalloc.stop()
                    print(f"Memory usage: Current - {current / 10**6:.4f} MB, Peak - {peak / 10**6:.4f} MB")
                    print(f"Tìm thấy lời giải trong {end_time - start_time:.4f} giây.")
                    return solution
                else:
                    # Nếu không liên thông, thêm mệnh đề chặn lời giải này
                    blocking_clause = [-lit for lit in model if abs(lit) <= len(self.var_map)]
                    solver.add_clause(blocking_clause)

        end_time = time.time()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        print(f"Không tìm thấy lời giải liên thông. Thời gian: {end_time - start_time:.4f} giây.")
        print(f"Memory usage: Current - {current / 10**6:.4f} MB, Peak - {peak / 10**6:.4f} MB")
        return None

HashiSolver.solve_with_pysat = solve_with_pysat
HashiSolver._model_to_solution = _model_to_solution