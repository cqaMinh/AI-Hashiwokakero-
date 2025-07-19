import heapq
import time
from itertools import combinations, product
from pysat.solvers import Glucose4
from pysat.card import CardEnc, EncType

class HashiSolver:
    def __init__(self, grid):
        """
        Khởi tạo solver với một grid câu đố.
        """
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0])
        self.islands = []
        self.potential_bridges = []
        self._parse_grid()
        
        # Dùng để map các biến logic thành số nguyên cho SAT solver
        self.var_map = {}
        self.var_counter = 1

    def _parse_grid(self):
        """
        Phân tích grid đầu vào để tìm các đảo và các cây cầu tiềm năng.
        """
        # Tìm tất cả các đảo
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] > 0:
                    self.islands.append({'id': len(self.islands), 'r': r, 'c': c, 'val': self.grid[r][c]})

        # Tìm các cây cầu tiềm năng giữa các đảo
        for i1_idx, i1 in enumerate(self.islands):
            for i2_idx, i2 in enumerate(self.islands):
                if i1_idx >= i2_idx:
                    continue
                
                # Cùng hàng
                if i1['r'] == i2['r']:
                    is_clear = True
                    for c in range(min(i1['c'], i2['c']) + 1, max(i1['c'], i2['c'])):
                        if self.grid[i1['r']][c] > 0:
                            is_clear = False
                            break
                    if is_clear:
                        self.potential_bridges.append({'u': i1['id'], 'v': i2['id'], 'dir': 'h'})
                
                # Cùng cột
                if i1['c'] == i2['c']:
                    is_clear = True
                    for r in range(min(i1['r'], i2['r']) + 1, max(i1['r'], i2['r'])):
                        if self.grid[r][i2['c']] > 0:
                            is_clear = False
                            break
                    if is_clear:
                        self.potential_bridges.append({'u': i1['id'], 'v': i2['id'], 'dir': 'v'})
    
    def _get_var(self, bridge_idx, count):
        if (bridge_idx, count) not in self.var_map:
            self.var_map[(bridge_idx, count)] = self.var_counter
            self.var_counter += 1
        return self.var_map[(bridge_idx, count)]

    def _generate_cnf(self):
        clauses = []
        
        # 1. Ràng buộc: Hai cầu (count=2) ngụ ý một cầu (count=1)
        for i in range(len(self.potential_bridges)):
            v1 = self._get_var(i, 1)
            v2 = self._get_var(i, 2)
            # ¬v2 ∨ v1
            clauses.append([-v2, v1])

        # 2. Ràng buộc: Số lượng cầu chính xác cho mỗi đảo
        for island in self.islands:
            lits = []
            weights = []
            
            for i, bridge in enumerate(self.potential_bridges):
                if bridge['u'] == island['id'] or bridge['v'] == island['id']:
                    lits.append(self._get_var(i, 1))
                    lits.append(self._get_var(i, 2))
                    weights.append(1)
                    weights.append(1) # Trọng số cho v2 là 1 vì v2 => v1, tổng sẽ là 1+1=2

            # Mã hóa ràng buộc tổng bằng CardEnc của PySAT
            # Sum(lits) = island['val']
            card_clauses = CardEnc.equals(lits=lits, bound=island['val'], top_id=self.var_counter, encoding=EncType.seqcounter)
            clauses.extend(card_clauses.clauses)
            self.var_counter = card_clauses.nv

        # 3. Ràng buộc: Các cây cầu không được giao nhau
        for i, b1 in enumerate(self.potential_bridges):
            for j, b2 in enumerate(self.potential_bridges):
                if i >= j: continue
                if b1['dir'] == b2['dir']: continue

                # Xác định cầu ngang và cầu dọc
                h_bridge = b1 if b1['dir'] == 'h' else b2
                v_bridge = b2 if b1['dir'] == 'h' else b1
                h_idx = i if b1['dir'] == 'h' else j
                v_idx = j if b1['dir'] == 'h' else i
                
                i_h1, i_h2 = self.islands[h_bridge['u']], self.islands[h_bridge['v']]
                i_v1, i_v2 = self.islands[v_bridge['u']], self.islands[v_bridge['v']]

                # Kiểm tra xem chúng có giao nhau không
                crosses = (min(i_v1['r'], i_v2['r']) < i_h1['r'] < max(i_v1['r'], i_v2['r']) and
                           min(i_h1['c'], i_h2['c']) < i_v1['c'] < max(i_h1['c'], i_h2['c']))

                if crosses:
                    # Nếu có cầu ngang, không thể có cầu dọc và ngược lại
                    # ¬h_bridge ∨ ¬v_bridge
                    v_h = self._get_var(h_idx, 1)
                    v_v = self._get_var(v_idx, 1)
                    clauses.append([-v_h, -v_v])
                    
        return clauses

    def solve_with_pysat(self):
        print("--- Giải bằng PySAT ---")
        start_time = time.time()
        
        base_clauses = self._generate_cnf()
        
        with Glucose4(bootstrap_with=base_clauses) as solver:
            while solver.solve():
                model = solver.get_model()
                solution = self._model_to_solution(model)
                
                if self._is_connected(solution):
                    end_time = time.time()
                    print(f"Tìm thấy lời giải trong {end_time - start_time:.4f} giây.")
                    return solution
                else:
                    # Nếu không liên thông, thêm mệnh đề chặn lời giải này
                    blocking_clause = [-lit for lit in model if abs(lit) <= len(self.var_map)]
                    solver.add_clause(blocking_clause)

        end_time = time.time()
        print(f"Không tìm thấy lời giải liên thông. Thời gian: {end_time - start_time:.4f} giây.")
        return None
    
    def solve_with_backtracking(self):
        """Wrapper cho thuật toán Backtracking."""
        print("\n--- Giải bằng Backtracking ---")
        start_time = time.time()
        
        # Một assignment là một mảng, mỗi phần tử tương ứng với một cầu tiềm năng
        # giá trị là 0 (không cầu), 1 (một cầu), 2 (hai cầu)
        assignment = [0] * len(self.potential_bridges)
        solution = self._backtrack_recursive(assignment, 0)
        
        end_time = time.time()
        if solution:
            print(f"Tìm thấy lời giải trong {end_time - start_time:.4f} giây.")
        else:
            print(f"Không tìm thấy lời giải. Thời gian: {end_time - start_time:.4f} giây.")
        return solution

    def _backtrack_recursive(self, assignment, bridge_idx):
        # Nếu đã gán cho tất cả các cầu, kiểm tra xem có phải là lời giải cuối cùng
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

    def solve_with_a_star(self):
        """Wrapper cho thuật toán A*."""
        print("\n--- Giải bằng A* ---")
        start_time = time.time()

        initial_assignment = [-1] * len(self.potential_bridges)
        open_list = []
        heapq.heappush(open_list, (self._heuristic(initial_assignment), initial_assignment))
        visited = set()

        while open_list:
            f_score, current_assignment = heapq.heappop(open_list)

            if tuple(current_assignment) in visited:
               continue
            visited.add(tuple(current_assignment))
            # Tìm cầu đầu tiên chưa được "khóa" (giả sử gán từ trái qua phải)
            try:
                bridge_idx_to_assign = current_assignment.index(-1) # -1 là cờ chưa gán
            except ValueError: # Không còn -1, nghĩa là đã gán hết
                if self._is_valid_solution(current_assignment):
                    end_time = time.time()
                    print(f"Tìm thấy lời giải trong {end_time - start_time:.4f} giây.")
                    return current_assignment
                else:
                    continue
            
            # Tạo các trạng thái con
            for val in range(3):
                new_assignment = list(current_assignment)
                new_assignment[bridge_idx_to_assign] = val
                
                if self._is_partially_valid(new_assignment, bridge_idx_to_assign + 1):
                    g_score = bridge_idx_to_assign + 1
                    h_score = self._heuristic(new_assignment)
                    new_f_score = g_score + h_score
                    open_list.append((new_f_score, new_assignment))

        end_time = time.time()
        print(f"Không tìm thấy lời giải. Thời gian: {end_time - start_time:.4f} giây.")
        return None
    
    def _heuristic(self, assignment):
        """
        Hàm Heuristic cho A*.
        Ước tính số lượng ràng buộc bị vi phạm.
        Một heuristic đơn giản là tổng độ chênh lệch giữa số cầu yêu cầu và số cầu hiện tại.
        """
        h = 0
        island_bridges = [0] * len(self.islands)
        for i, val in enumerate(assignment):
            if val > 0:
                bridge = self.potential_bridges[i]
                island_bridges[bridge['u']] += val
                island_bridges[bridge['v']] += val
        
        for i, island in enumerate(self.islands):
            h += abs(island['val'] - island_bridges[i])
        return h


    def solve_with_brute_force(self):
        """Giải bằng Brute-Force. Chỉ dùng cho so sánh trên các grid nhỏ."""
        print("\n--- Giải bằng Brute-Force ---")
        start_time = time.time()

        # Tạo mọi tổ hợp có thể của các giá trị cầu (0, 1, 2)
        num_bridges = len(self.potential_bridges)

        for assignment_tuple in product(range(3), repeat=num_bridges):
            assignment = list(assignment_tuple)
            if self._is_valid_solution(assignment):
                end_time = time.time()
                print(f"Tìm thấy lời giải trong {end_time - start_time:.4f} giây.")
                return assignment

        end_time = time.time()
        print(f"Không tìm thấy lời giải. Thời gian: {end_time - start_time:.4f} giây.")
        return None

    
    def _is_partially_valid(self, assignment, num_assigned):
        """Kiểm tra xem một assignment một phần có hợp lệ không (dùng để cắt tỉa)."""
        # Kiểm tra số lượng cầu không vượt quá yêu cầu
        island_bridges = [0] * len(self.islands)
        for i in range(num_assigned):
            val = assignment[i]
            if val > 0:
                bridge = self.potential_bridges[i]
                island_bridges[bridge['u']] += val
                island_bridges[bridge['v']] += val
        
        for i, island in enumerate(self.islands):
            if island_bridges[i] > island['val']:
                return False
        
        # Có thể thêm kiểm tra giao nhau ở đây để cắt tỉa tốt hơn
        return True

    def _is_valid_solution(self, assignment):
        """
        Kiểm tra xem một assignment hoàn chỉnh có phải là một lời giải hợp lệ không.
        Assignment: một danh sách các giá trị (0, 1, 2) cho mỗi cầu tiềm năng.
        """
        # 1. Kiểm tra số lượng cầu
        island_bridges = [0] * len(self.islands)
        for i, val in enumerate(assignment):
            if val > 0:
                bridge = self.potential_bridges[i]
                island_bridges[bridge['u']] += val
                island_bridges[bridge['v']] += val
        
        for i, island in enumerate(self.islands):
            if island_bridges[i] != island['val']:
                return False

        # 2. Kiểm tra giao nhau
        active_bridges = [i for i, val in enumerate(assignment) if val > 0]
        for b1_idx_ptr, b1_g_idx in enumerate(active_bridges):
             for b2_g_idx in active_bridges[b1_idx_ptr+1:]:
                b1 = self.potential_bridges[b1_g_idx]
                b2 = self.potential_bridges[b2_g_idx]
                if b1['dir'] == b2['dir']: continue

                h_bridge = b1 if b1['dir'] == 'h' else b2
                v_bridge = b2 if b1['dir'] == 'h' else b1
                i_h1, i_h2 = self.islands[h_bridge['u']], self.islands[h_bridge['v']]
                i_v1, i_v2 = self.islands[v_bridge['u']], self.islands[v_bridge['v']]
                
                crosses = (min(i_v1['r'], i_v2['r']) < i_h1['r'] < max(i_v1['r'], i_v2['r']) and
                           min(i_h1['c'], i_h2['c']) < i_v1['c'] < max(i_h1['c'], i_h2['c']))
                if crosses:
                    return False
        
        # 3. Kiểm tra tính liên thông
        if not self._is_connected(assignment):
            return False

        return True
        
    def _is_connected(self, solution):
        """
        Kiểm tra xem đồ thị có liên thông không bằng BFS/DFS.
        Solution: assignment từ Backtracking/A* hoặc model từ PySAT.
        """
        if not self.islands: return True
        
        # Xây dựng danh sách kề
        adj = {i: [] for i in range(len(self.islands))}
        active_island_found = False
        
        if isinstance(solution, list): # Assignment từ các thuật toán tự triển khai
             for i, val in enumerate(solution):
                if val > 0:
                    bridge = self.potential_bridges[i]
                    adj[bridge['u']].append(bridge['v'])
                    adj[bridge['v']].append(bridge['u'])
                    active_island_found = True
        else: # Model từ PySAT
            for (bridge_idx, count), var_num in self.var_map.items():
                if solution[var_num-1] > 0 and count == 1:
                    bridge = self.potential_bridges[bridge_idx]
                    adj[bridge['u']].append(bridge['v'])
                    adj[bridge['v']].append(bridge['u'])
                    active_island_found = True

        if not active_island_found: # Nếu không có cầu nào
            return len(self.islands) <= 1

        # Bắt đầu duyệt đồ thị (BFS)
        q = [0]
        visited = {0}
        count = 0
        while q:
            u = q.pop(0)
            count += 1
            for v in adj[u]:
                if v not in visited:
                    visited.add(v)
                    q.append(v)
        
        return count == len(self.islands)

    def _model_to_solution(self, model):
        """Chuyển đổi model từ PySAT thành định dạng assignment."""
        assignment = [0] * len(self.potential_bridges)
        # Tạo map ngược từ var_num -> (bridge_idx, count)
        rev_var_map = {v: k for k, v in self.var_map.items()}
        
        for lit in model:
            if lit > 0 and lit in rev_var_map:
                bridge_idx, count = rev_var_map[lit]
                if count == 2:
                    assignment[bridge_idx] = 2
                elif count == 1 and assignment[bridge_idx] == 0: # Chỉ gán 1 nếu chưa được gán 2
                    assignment[bridge_idx] = 1
        return assignment

    def print_solution(self, solution):
        """In ra grid lời giải."""
        if not solution:
            print("Không có lời giải để hiển thị.")
            return

        display_grid = [['0'] * self.cols for _ in range(self.rows)]
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] > 0:
                    display_grid[r][c] = str(self.grid[r][c])

        for i, val in enumerate(solution):
            if val > 0:
                bridge = self.potential_bridges[i]
                i1 = self.islands[bridge['u']]
                i2 = self.islands[bridge['v']]
                
                if bridge['dir'] == 'h':
                    char = '=' if val == 2 else '-'
                    for c in range(min(i1['c'], i2['c']) + 1, max(i1['c'], i2['c'])):
                        display_grid[i1['r']][c] = char
                else: # vertical
                    char = '$' if val == 2 else '|'
                    for r in range(min(i1['r'], i2['r']) + 1, max(i1['r'], i2['r'])):
                        display_grid[r][i1['c']] = char
        
        print("\nLời giải:")
        for row in display_grid:
            print("[ " + " , ".join([f'"{c}"' for c in row]) + " ]")

    def print_solution_to_file(self, solution, filename):
        """In ra lời giải vào tệp."""

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

    input_file = 'input1.txt'
    grid_data = load_grid_from_file(input_file)

    if grid_data:
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
        initial_assignment = [-1] * len(solver_astar.potential_bridges)
        solution_astar = solver_astar.solve_with_a_star()
        solver_astar.print_solution(solution_astar)
        print("\n" + "="*50)

        # Giải bằng Brute-Force 
        solver_bf = HashiSolver(grid_data)
        solution_bf = solver_bf.solve_with_brute_force()
        solver_bf.print_solution(solution_bf)
