from hashiclass import HashiSolver
import time
import heapq
import tracemalloc
from collections import defaultdict
from itertools import combinations

class UnionFind:
    def __init__(self, size):
        self.parent = list(range(size))
        self.rank = [0] * size
        self.count = size
    
    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    
    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px == py:
            return
        if self.rank[px] < self.rank[py]:
            px, py = py, px
        self.parent[py] = px
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1
        self.count -= 1
    
    def components(self):
        return self.count

def define_variables(self):
    var_map = {}
    var_count = 0
    max_bridges = {island['id']: island['val'] for island in self.islands}
    valid_bridges = []
    bridges = []
    for bridge in self.potential_bridges:
        u, v = bridge['u'], bridge['v']
        i1, i2 = self.islands[u], self.islands[v]
        x1, y1 = i1['r'], i1['c']
        x2, y2 = i2['r'], i2['c']
        bridges.append((x1, y1, x2, y2, bridge['dir']))
    
    for bridge in bridges:
        x1, y1, x2, y2, _ = bridge
        u = next(i['id'] for i in self.islands if i['r'] == x1 and i['c'] == y1)
        v = next(i['id'] for i in self.islands if i['r'] == x2 and i['c'] == y2)
        if max_bridges[u] > 0 and max_bridges[v] > 0:
            var_map[(bridge, 1)] = var_count + 1
            var_count += 1
            if max_bridges[u] >= 2 and max_bridges[v] >= 2:
                var_map[(bridge, 2)] = var_count + 1
                var_count += 1
            valid_bridges.append(bridge)
    
    #print(f"var_map: {var_map}")
    #print(f"valid_bridges: {valid_bridges}")
    return var_map, var_count, valid_bridges

def generate_cnf_astar(self):
    var_map, _, valid_bridges = self.define_variables()
    clauses = []
    clause_to_vars = defaultdict(list)
    island_bridges = defaultdict(list)
    island_positions = {(island['r'], island['c']) for island in self.islands}
    
    for bridge in valid_bridges:
        x1, y1, x2, y2, _ = bridge
        island_bridges[(x1, y1)].append(bridge)
        island_bridges[(x2, y2)].append(bridge)
    
    #print(f"island_bridges: {dict(island_bridges)}")
    
    for island in self.islands:
        x, y, val = island['r'], island['c'], island['val']
        bridge_vars = [(var_map[(b, n)], n) for b in island_bridges[(x, y)] for n in [1, 2] if (b, n) in var_map]
        
        #print(f"Island ({x}, {y}, val={val}): vars={bridge_vars}")
        
        if not bridge_vars and val > 0:
            print(f"Warning: Island ({x}, {y}) with degree {val} has no possible bridges")
            clauses.append([0])
            continue
        
        max_possible = sum(w for _, w in bridge_vars)
        if max_possible < val:
            print(f"Warning: Island ({x}, {y}) requires {val} but max possible is {max_possible}")
            clauses.append([0])
            continue
        
        for k in range(val + 1, max_possible + 1):
            for comb in combinations([v for v, _ in bridge_vars], k):
                clause = [-v for v in comb]
                clauses.append(clause)
                clause_to_vars[len(clauses) - 1] = [abs(v) for v in comb]
        
        if val > 0:
            clause = [v for v, _ in bridge_vars]
            clauses.append(clause)
            clause_to_vars[len(clauses) - 1] = [v for v, _ in bridge_vars]
        
        if val > 1:
            for comb in combinations([v for v, _ in bridge_vars], val):
                clause = [-v for v in comb]
                clauses.append(clause)
                clause_to_vars[len(clauses) - 1] = [abs(v) for v in comb]
    
    for bridge in valid_bridges:
        if (bridge, 1) in var_map and (bridge, 2) in var_map:
            v1, v2 = var_map[(bridge, 1)], var_map[(bridge, 2)]
            clause = [-v1, -v2]
            clauses.append(clause)
            clause_to_vars[len(clauses) - 1] = [v1, v2]
    
    for i, b1 in enumerate(valid_bridges):
        for b2 in valid_bridges[i + 1:]:
            if b1[4] != b2[4]:
                if b1[4] == 'h' and b2[4] == 'v':
                    h_bridge, v_bridge = b1, b2
                elif b1[4] == 'v' and b2[4] == 'h':
                    h_bridge, v_bridge = b2, b1
                else:
                    continue
                x1, y1, x2, y2 = h_bridge[:4]
                x3, y3, x4, y4 = v_bridge[:4]
                if x3 < x1 < x4 and y1 < y3 < y2 and (x1, y3) not in island_positions:
                    for n1 in [1, 2]:
                        for n2 in [1, 2]:
                            if (b1, n1) in var_map and (b2, n2) in var_map:
                                clause = [-var_map[(b1, n1)], -var_map[(b2, n2)]]
                                clauses.append(clause)
                                clause_to_vars[len(clauses) - 1] = [var_map[(b1, n1)], var_map[(b2, n2)]]
    
    #print(f"Generated {len(clauses)} CNF clauses")
    return clauses, clause_to_vars, var_map, valid_bridges

def compute_island_degrees(self, assignment, var_map):
    degrees = defaultdict(int)
    for (bridge, num), var in var_map.items():
        if var in assignment:
            x1, y1, x2, y2, _ = bridge
            degrees[(x1, y1)] += num
            degrees[(x2, y2)] += num
    #print(f"Degrees: {dict(degrees)}")
    return degrees

def evaluate_cnf(self, clauses, assignment, clause_status, clause_to_vars, changed_var=None):
    if clause_status is None:
        clause_status = [False] * len(clauses)
        clauses_to_check = range(len(clauses))
    else:
        clauses_to_check = set()
        if changed_var:
            for clause_idx in clause_to_vars[changed_var]:
                clauses_to_check.add(clause_idx)
        else:
            clauses_to_check = range(len(clauses))
    
    satisfied = sum(1 for i in range(len(clauses)) if clause_status[i])
    for i in clauses_to_check:
        if clause_status[i]:
            continue
        for lit in clauses[i]:
            if lit > 0 and lit in assignment:
                clause_status[i] = True
                satisfied += 1
                break
            elif lit < 0 and -lit not in assignment:
                clause_status[i] = True
                satisfied += 1
                break
    return satisfied, clause_status

def prioritize_variables(self, var_map):
    island_degrees = {(island['r'], island['c']): island['val'] for island in self.islands}
    var_priority = []
    for (bridge, num), var in var_map.items():
        x1, y1, x2, y2, _ = bridge
        priority = min(island_degrees[(x1, y1)], island_degrees[(x2, y2)]) + (2 if num == 2 else 1)
        var_priority.append((priority, var))
    return [var for _, var in sorted(var_priority, reverse=True)]

def compute_connectivity(self, assignment, var_map):
    island_to_idx = {(island['r'], island['c']): i for i, island in enumerate(self.islands)}
    uf = UnionFind(len(self.islands))
    for (bridge, num), var in var_map.items():
        if var in assignment:
            x1, y1, x2, y2, _ = bridge
            uf.union(island_to_idx[(x1, y1)], island_to_idx[(x2, y2)])
    return uf.components()

def a_star_search(self, clauses, clause_to_vars, var_map, valid_bridges):
    open_set = [(0, set(), 0, [False] * len(clauses), 0)]  # (f_score, assignment, g_score, clause_status, state_id)
    closed = set()
    total_required = sum(island['val'] for island in self.islands)
    island_to_idx = {(island['r'], island['c']): i for i, island in enumerate(self.islands)}
    prioritized_vars = self.prioritize_variables(var_map)
    state_id = 0
    
    while open_set:
        f_score, assignment, g_score, clause_status, _ = heapq.heappop(open_set)
        
        if tuple(sorted(assignment)) in closed:
            continue
        
        degrees = self.compute_island_degrees(assignment, var_map)
        if any(degrees[(island['r'], island['c'])] > island['val'] for island in self.islands):
            #print(f"Pruned: Exceeded degree at {[(island['r'], island['c'], degrees[(island['r'], island['c'])], island['val']) for island in self.islands if degrees[(island['r'], island['c'])] > island['val']]}")
            continue
        
        satisfied, _ = self.evaluate_cnf(clauses, assignment, clause_status, clause_to_vars)
        if satisfied == len(clauses):
            valid = all(degrees[(island['r'], island['c'])] == island['val'] for island in self.islands)
            components = self.compute_connectivity(assignment, var_map)
            if valid and components == 1:
                return assignment
        
        closed.add(tuple(sorted(assignment)))
        
        remaining_degrees = sum(max(0, island['val'] - degrees[(island['r'], island['c'])]) for island in self.islands)
        assigned = sum(num for (b, num), v in var_map.items() if v in assignment)
        if remaining_degrees > total_required - assigned:
            #print(f"Pruned: remaining_degrees={remaining_degrees} > total_required-assigned={total_required-assigned}")
            continue
        
        components = self.compute_connectivity(assignment, var_map)
        assigned_bridges = sum(1 for (b, num), v in var_map.items() if v in assignment)
        if components > len(self.islands) - assigned_bridges + 1:
            #print(f"Pruned: components={components} > {len(self.islands) - assigned_bridges + 1}")
            continue
        
        for var in prioritized_vars:
            if var not in assignment and -var not in assignment:
                new_assignment = assignment | {var}
                new_g_score = g_score + 1
                new_satisfied, new_clause_status = self.evaluate_cnf(clauses, new_assignment, clause_status.copy(), clause_to_vars, var)
                unsatisfied = len(clauses) - new_satisfied
                new_components = self.compute_connectivity(new_assignment, var_map)
                remaining = max(0, remaining_degrees - sum(num for (b, num), v in var_map.items() if v == var))
                degree_penalty = sum(max(0, island['val'] - degrees[(island['r'], island['c'])]) for island in self.islands)
                h_score = unsatisfied + remaining + max(0, new_components - 1) + degree_penalty
                #print(f"Exploring var {var}, f_score={new_g_score + h_score}, h_score={h_score}")
                state_id += 1
                heapq.heappush(open_set, (new_g_score + h_score, new_assignment, new_g_score, new_clause_status, state_id))
    
    return None

def solve_with_a_star(self):
    print("\n--- Giải bằng A* ---")
    start_time = time.time()
    tracemalloc.start()
    
    clauses, clause_to_vars, var_map, valid_bridges = self.generate_cnf_astar()
    assignment = self.a_star_search(clauses, clause_to_vars, var_map, valid_bridges)
    
    if assignment:
        result = [0] * len(self.potential_bridges)
        for (bridge, num), var in var_map.items():
            if var in assignment:
                x1, y1, x2, y2, dir = bridge
                u = next(i['id'] for i in self.islands if i['r'] == x1 and i['c'] == y1)
                v = next(i['id'] for i in self.islands if i['r'] == x2 and i['c'] == y2)
                if u > v:
                    u, v = v, u
                    x1, y1, x2, y2 = x2, y2, x1, y1
                for idx, pb in enumerate(self.potential_bridges):
                    if pb['u'] == u and pb['v'] == v and pb['dir'] == dir:
                        result[idx] = max(result[idx], num)
                        break
        #print(f"Raw assignment: {assignment}")
        #print(f"Converted solution: {result}")
        end_time = time.time()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        print(f"Tìm thấy lời giải trong {end_time - start_time:.4f} giây.")
        print(f"Memory usage: Current - {current / 10**6:.4f} MB, Peak - {peak / 10**6:.4f} MB")
        return result
    
    end_time = time.time()
    print(f"Không tìm thấy lời giải. Thời gian: {end_time - start_time:.4f} giây.")
    return None

HashiSolver.define_variables = define_variables
HashiSolver.generate_cnf_astar = generate_cnf_astar
HashiSolver.compute_island_degrees = compute_island_degrees
HashiSolver.evaluate_cnf = evaluate_cnf
HashiSolver.prioritize_variables = prioritize_variables
HashiSolver.compute_connectivity = compute_connectivity
HashiSolver.a_star_search = a_star_search
HashiSolver.solve_with_a_star = solve_with_a_star