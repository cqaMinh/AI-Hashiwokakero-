from operator import index
from hashiclass import HashiSolver
import time 
import tracemalloc

#chuquocanhminh

def _backtrack_recursive(self, assignment, bridge_idx):
        if bridge_idx == len(self.potential_bridges):
            if self._is_valid_solution(assignment):
                return assignment
            return None

        # Thử gán các giá trị (0, 1, 2) cho cây cầu hiện tại
        for val in range(3):
            assignment[bridge_idx] = val
            
            # Cắt tỉa: Kiểm tra sớm các vi phạm
            if self._is_partially_valid(assignment, bridge_idx + 1):
                result = self._backtrack_recursive(assignment, bridge_idx + 1)
                if result:
                    return result
        
        # Quay lui
        assignment[bridge_idx] = 0
        return None

def solve_with_backtracking(self):
        print("\n--- Giải bằng Backtracking ---")
        start_time = time.time()
        tracemalloc.start()
        

        assignment = [0] * len(self.potential_bridges)
        solution = self._backtrack_recursive(assignment, 0)
        
        end_time = time.time()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        if solution:
            print(f"Tìm thấy lời giải trong {end_time - start_time:.4f} giây.")
            print(f"Memory usage: Current - {current / 10**6:.4f} MB, Peak - {peak / 10**6:.4f} MB")
        else:
            print(f"Không tìm thấy lời giải. Thời gian: {end_time - start_time:.4f} giây.")
        print(f"Memory usage: Current - {current / 10**6:.4f} MB, Peak - {peak / 10**6:.4f} MB")
        return solution


def solve_with_brute_force(self):
    print("\n--- Giải bằng Brute-Force ---")
    n = len(self.potential_bridges)
    start_time = time.time()
    tracemalloc.start()
    assignment = [0] * n

    def backtrack(index):
        if index == n:
            if self._is_valid_solution(assignment):
                return assignment
            return None
            
        for val in range(3):
            assignment[index] = val
            if self._is_partially_valid(assignment, index + 1):
                result = backtrack(index + 1)
                if result:
                    return result
            
        assignment[index] = 0
        
    if backtrack(0):
        end_time = time.time()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        print(f"Tìm thấy lời giải trong {end_time - start_time:.4f} giây.")
        print(f"Memory usage: Current - {current / 10**6:.4f} MB, Peak - {peak / 10**6:.4f} MB")
        return assignment
    else:
        print("Không tìm được lời giải.")

HashiSolver.solve_with_backtracking = solve_with_backtracking
HashiSolver.solve_with_brute_force = solve_with_brute_force
HashiSolver._backtrack_recursive = _backtrack_recursive

