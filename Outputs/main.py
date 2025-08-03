import os
import time
from hashiclass import HashiSolver
from helper01 import _backtrack_recursive, solve_with_backtracking, solve_with_brute_force
from helper02 import solve_with_a_star
from helper03 import solve_with_pysat, _model_to_solution

def load_grid_from_file(filename):
    import os
    
    try:
        with open('../Inputs/' + filename, 'r') as f:
            grid = []
            for line in f:
                grid.append([int(x) for x in line.strip().split(',')])
            return grid
    except FileNotFoundError:
        print(f"Lỗi: không tìm thấy tệp '{filename}'")
        return None
    except ValueError:
        print(f"Lỗi: tệp '{filename}' chứa dữ liệu không hợp lệ.")
        return None


if __name__ == '__main__':
    input_file = '../Inputs/input-01.txt'
    grid_data = load_grid_from_file(input_file)

    if grid_data:
        print("map:" + input_file)

        #Giải bằng PySAT 
        solver_pysat = HashiSolver(grid_data)
        solution_pysat = solver_pysat.solve_with_pysat()
        solver_pysat.print_solution(solution_pysat)
        print("\n" + "="*50)
        
        #Giải bằng Backtracking
        solver_backtrack = HashiSolver(grid_data)
        solution_backtrack = solver_backtrack.solve_with_backtracking()
        solver_backtrack.print_solution(solution_backtrack)
        print("\n" + "="*50)
        
        # Giải bằng A*
        solver_astar = HashiSolver(grid_data)
        solution_astar = solver_astar.solve_with_a_star()
        solver_astar.print_solution(solution_astar)
        print("\n" + "="*50)

        # Giải bằng Brute-Force 
        solver_bf = HashiSolver(grid_data)
        solution_bf = solver_bf.solve_with_brute_force()
        solver_bf.print_solution(solution_bf)
