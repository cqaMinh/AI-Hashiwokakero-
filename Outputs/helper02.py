from hashiclass import HashiSolver
import time
import heapq

#nguyenanhhoang

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
    
HashiSolver.solve_with_a_star = solve_with_a_star
HashiSolver._heuristic = _heuristic