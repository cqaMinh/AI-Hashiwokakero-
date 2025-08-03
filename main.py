import os
import time
from hashiclass import HashiSolver
from helper01 import _backtrack_recursive, solve_with_backtracking, solve_with_brute_force
from helper02 import solve_with_a_star
from helper03 import solve_with_pysat, _model_to_solution

def load_grid_from_file(filename):
    try:
        with open('Inputs/' + filename, 'r') as f:
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

def save_solution_to_file(filename, grid_data, solutions):
    os.makedirs('Outputs', exist_ok=True)
    
    output_filename = f"Outputs/output-{filename}"
    
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(f"map: {filename}\n\n")
        
        for solver_name, solution in solutions:
            f.write(f"--- {solver_name} ---\n")
            if solution:
                f.write("Lời giải:\n")
                display_grid = [['0'] * len(grid_data[0]) for _ in range(len(grid_data))]
                for r in range(len(grid_data)):
                    for c in range(len(grid_data[0])):
                        if grid_data[r][c] > 0:
                            display_grid[r][c] = str(grid_data[r][c])
                
                solver = HashiSolver(grid_data)
                for i, val in enumerate(solution):
                    if val > 0:
                        bridge = solver.potential_bridges[i]
                        i1 = solver.islands[bridge['u']]
                        i2 = solver.islands[bridge['v']]
                        if bridge['dir'] == 'h':
                            char = '=' if val == 2 else '-'
                            for c in range(min(i1['c'], i2['c']) + 1, max(i1['c'], i2['c'])):
                                display_grid[i1['r']][c] = char
                        else: 
                            char = '$' if val == 2 else '|'
                            for r in range(min(i1['r'], i2['r']) + 1, max(i1['r'], i2['r'])):
                                display_grid[r][i1['c']] = char
                
                for row in display_grid:
                    f.write("[ " + " , ".join([f'"{c}"' for c in row]) + " ]\n")
            else:
                f.write("Không tìm thấy lời giải.\n")
            f.write("\n" + "="*50 + "\n")

if __name__ == '__main__':
    input_file = input("Nhập tên file đầu vào (ví dụ: input-01.txt): ").strip()
    grid_data = load_grid_from_file(input_file)

    if grid_data:
        print(f"map: {input_file}")
        solutions = []

        print("\nChọn thuật toán để chạy:")
        print("1: PySAT")
        print("2: Backtracking")
        print("3: A*")
        print("4: Brute-Force")
        print("5: Tất cả")
        choice = input("Nhập số (1-5): ").strip()

        algorithms = []
        if choice == '5':
            algorithms = [('PySAT', 'solve_with_pysat'), 
                         ('Backtracking', 'solve_with_backtracking'), 
                         ('A*', 'solve_with_a_star'), 
                         ('Brute-Force', 'solve_with_brute_force')]
        elif choice == '1':
            algorithms = [('PySAT', 'solve_with_pysat')]
        elif choice == '2':
            algorithms = [('Backtracking', 'solve_with_backtracking')]
        elif choice == '3':
            algorithms = [('A*', 'solve_with_a_star')]
        elif choice == '4':
            algorithms = [('Brute-Force', 'solve_with_brute_force')]
        else:
            print("Lựa chọn không hợp lệ, chạy tất cả thuật toán.")
            algorithms = [('PySAT', 'solve_with_pysat'), 
                         ('Backtracking', 'solve_with_backtracking'), 
                         ('A*', 'solve_with_a_star'), 
                         ('Brute-Force', 'solve_with_brute_force')]

        for solver_name, solver_method in algorithms:
            solver = HashiSolver(grid_data)
            solution = getattr(solver, solver_method)()
            solver.print_solution(solution)
            solutions.append((solver_name, solution))
            print("\n" + "="*50)

        save_solution_to_file(input_file, grid_data, solutions)
