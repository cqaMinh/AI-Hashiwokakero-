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
        self.potential_bridges = [] #
        self._parse_grid()
        
        # Dùng để map các biến logic thành số nguyên cho SAT solver
        self.var_map = {}
        self.var_counter = 1

    def _parse_grid(self):
        """
        Phân tích lưới đầu vào để:
        1. Xác định vị trí các đảo.
        cd2. Tìm các cặp đảo có thể nối cầu (cùng hàng hoặc cột, không bị chắn).
        """

    #Xác định tất cả các đảo trên lưới ===
        island_id = 0
        for row in range(self.rows):
            for col in range(self.cols):
                cell_value = self.grid[row][col]
                if cell_value > 0:  # Nếu là đảo (số cầu cần kết nối)
                    island = {
                        'id': island_id,
                        'r': row,
                        'c': col,
                        'val': cell_value  # số lượng cầu cần nối
                    }
                    self.islands.append(island)
                    island_id += 1

        #Tìm các cặp đảo có thể nối bằng cầu ===
        for i in range(len(self.islands)):
            island_a = self.islands[i]
            for j in range(i + 1, len(self.islands)):
                island_b = self.islands[j]

                # Nếu 2 đảo cùng hàng
                if island_a['r'] == island_b['r']:
                    row = island_a['r']
                    col_start = min(island_a['c'], island_b['c']) + 1
                    col_end = max(island_a['c'], island_b['c'])

                # Kiểm tra giữa 2 đảo có bị chắn không
                    clear = all(self.grid[row][c] == 0 for c in range(col_start, col_end))
                    if clear:
                        self.potential_bridges.append({
                            'u': island_a['id'],
                            'v': island_b['id'],
                            'dir': 'h'  # hướng ngang (horizontal)
                        })

                # Nếu 2 đảo cùng cột
                if island_a['c'] == island_b['c']:
                    col = island_a['c']
                    row_start = min(island_a['r'], island_b['r']) + 1
                    row_end = max(island_a['r'], island_b['r'])

                    # Kiểm tra giữa 2 đảo có bị chắn không
                    clear = all(self.grid[r][col] == 0 for r in range(row_start, row_end))
                    if clear:
                        self.potential_bridges.append({
                            'u': island_a['id'],
                            'v': island_b['id'],
                            'dir': 'v'  # hướng dọc (vertical)
                        })

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
        pass
    def solve_with_backtracking(self):
        pass
    def _backtrack_recursive(self, assignment, bridge_idx):
        pass
    def solve_with_a_star(self):
        pass
    def _heuristic(self, assignment):
        pass
    def solve_with_brute_force(self):
        pass
    def _is_partially_valid(self, assignment, num_assigned):
        """Kiểm tra xem một assignment một phần có hợp lệ không (dùng để cắt tỉa)."""
        # 1. Kiểm tra số lượng cầu không vượt quá yêu cầu
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
        
        # === BẮT ĐẦU ĐOẠN MÃ MỚI ĐỂ THÊM VÀO ===
        # 2. KIỂM TRA GIAO NHAU SỚM CHO CÁC CẦU ĐÃ GÁN
        # Lấy chỉ số của các cầu đã được xây (giá trị > 0)
        active_bridges_indices = [i for i, val in enumerate(assignment[:num_assigned]) if val > 0]
        
        # So sánh từng cặp cầu đang hoạt động
        for i in range(len(active_bridges_indices)):
            for j in range(i + 1, len(active_bridges_indices)):
                b1_idx = active_bridges_indices[i]
                b2_idx = active_bridges_indices[j]

                b1 = self.potential_bridges[b1_idx]
                b2 = self.potential_bridges[b2_idx]

                # Bỏ qua nếu cả hai cùng hướng
                if b1['dir'] == b2['dir']:
                    continue

                # Xác định cầu ngang và dọc
                h_bridge = b1 if b1['dir'] == 'h' else b2
                v_bridge = b2 if b1['dir'] == 'h' else b1
                
                i_h1, i_h2 = self.islands[h_bridge['u']], self.islands[h_bridge['v']]
                i_v1, i_v2 = self.islands[v_bridge['u']], self.islands[v_bridge['v']]

                # Kiểm tra xem chúng có cắt nhau không
                crosses = (min(i_v1['r'], i_v2['r']) < i_h1['r'] < max(i_v1['r'], i_v2['r']) and
                           min(i_h1['c'], i_h2['c']) < i_v1['c'] < max(i_h1['c'], i_h2['c']))
                
                if crosses:
                    return False  # Tìm thấy giao nhau -> nhánh này không hợp lệ, cắt tỉa ngay
        # === KẾT THÚC ĐOẠN MÃ MỚI ===

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
        pass
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

    def count_number_of_islands(self):
        count = 0
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] > 0 and not any(island['r'] == r and island['c'] == c for island in self.islands):
                    count += 1
        return count 
    
