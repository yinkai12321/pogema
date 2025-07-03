import numpy as np
from pogema import GridConfig

from heapq import heappop, heappush

INF = 1e7


class GridMemory:
    def __init__(self, start_r=64):
        self._memory = np.zeros(shape=(start_r * 2 + 1, start_r * 2 + 1), dtype=np.bool_)
        self._stocks_memory = np.zeros(shape=(start_r * 2 + 1, start_r * 2 + 1), dtype=np.bool_)
        self._directions_memory = np.zeros(shape=(start_r * 2 + 1, start_r * 2 + 1), dtype=np.int32)

    @staticmethod
    def _try_to_insert(x, y, source, target):
        r = source.shape[0] // 2
        try:
            target[x - r:x + r + 1, y - r:y + r + 1] = source
            return True
        except ValueError:
            return False

    def _increase_memory(self):
        m = self._memory
        s = self._stocks_memory
        d = self._directions_memory
        r = self._memory.shape[0]
        self._memory = np.zeros(shape=(r * 2 + 1, r * 2 + 1))
        self._stocks_memory = np.zeros(shape=(r * 2 + 1, r * 2 + 1))
        self._directions_memory = np.zeros(shape=(r * 2 + 1, r * 2 + 1), dtype=np.int32)
        assert self._try_to_insert(r, r, m, self._memory)
        assert self._try_to_insert(r, r, s, self._stocks_memory)
        assert self._try_to_insert(r, r, d, self._directions_memory)

    def update(self, x, y, obstacles, stocks=None, directions=None):
        while True:
            r = self._memory.shape[0] // 2
            if self._try_to_insert(r + x, r + y, obstacles, self._memory):
                if stocks is not None:
                    self._try_to_insert(r + x, r + y, stocks, self._stocks_memory)
                if directions is not None:
                    self._try_to_insert(r + x, r + y, directions, self._directions_memory)
                break
            self._increase_memory()

    def is_obstacle(self, x, y):
        r = self._memory.shape[0] // 2
        if -r <= x <= r and -r <= y <= r:
            return self._memory[r + x, r + y]
        else:
            return False

    def has_stocks(self, x, y):
        """检查指定位置是否有货物"""
        r = self._stocks_memory.shape[0] // 2
        if -r <= x <= r and -r <= y <= r:
            return self._stocks_memory[r + x, r + y]
        else:
            return False

    def can_pass(self, x, y, vehicle_type='standard'):
        """
        根据车辆类型判断是否可以通过指定位置
        :param x, y: 位置坐标
        :param vehicle_type: 车辆类型 ('small', 'standard', 'heavy')
        :return: True if can pass, False otherwise
        """
        # 首先检查是否是真正的障碍物（所有车辆都不能通过）
        if self.is_obstacle(x, y):
            return False
        
        # 然后检查是否有货物
        if self.has_stocks(x, y):
            # 根据车辆类型和货物类型判断通行能力
            # 这里可以扩展为更复杂的逻辑
            vehicle_capabilities = {
                'small': True,      # 小车可以通过货物位置
                'standard': False,  # 标准车不能通过货物位置
                'heavy': False,     # 重型车不能通过货物位置
            }
            return vehicle_capabilities.get(vehicle_type, False)
        
        # 如果既不是障碍物也没有货物，则可以通过
        return True

    def get_direction_type(self, x, y):
        """获取指定位置的方向类型"""
        r = self._directions_memory.shape[0] // 2
        if -r <= x <= r and -r <= y <= r:
            return self._directions_memory[r + x, r + y]
        else:
            return 0  # 默认为全方向

    def is_move_valid_by_direction(self, from_x, from_y, to_x, to_y):
        """
        根据方向限制检查移动是否有效
        :param from_x, from_y: 起始位置
        :param to_x, to_y: 目标位置
        :return: True if valid, False otherwise
        """
        direction_type = self.get_direction_type(from_x, from_y)
        
        dx = to_x - from_x
        dy = to_y - from_y
        
        # 检查是否为相邻移动
        if abs(dx) + abs(dy) != 1:
            return False
            
        if direction_type == 0:  # 全方向
            return True
        elif direction_type == 1:  # 左右方向
            return dy != 0 and dx == 0  # 只能左右移动
        elif direction_type == 2:  # 上下方向
            return dx != 0 and dy == 0  # 只能上下移动
        
        return False


class Node:
    def __init__(self, coord=None, g: int = 0, h: int = 0):
        if coord is None:
            coord = (INF, INF)
        self.i, self.j = coord
        self.g = g
        self.h = h
        self.f = g + h

    def __lt__(self, other):
        if self.f != other.f:
            return self.f < other.f
        elif self.g != other.g:
            return self.g < other.g
        else:
            return self.i < other.i or self.j < other.j


def h(node, target):
    nx, ny = node
    tx, ty = target
    return abs(nx - tx) + abs(ny - ty)


def a_star_vehicle_aware(start, target, grid: GridMemory, vehicle_type='standard', max_steps=10000):
    """
    支持车辆类型和方向限制的A*算法
    :param start: 起始位置
    :param target: 目标位置
    :param grid: 网格内存
    :param vehicle_type: 车辆类型 ('small', 'standard', 'heavy')
    :param max_steps: 最大搜索步数
    :return: 路径列表
    """
    open_ = list()
    closed = {start: None}

    heappush(open_, Node(start, 0, h(start, target)))

    for step in range(int(max_steps)):
        u = heappop(open_)

        for n in [(u.i - 1, u.j), (u.i + 1, u.j), (u.i, u.j - 1), (u.i, u.j + 1)]:
            # 检查车辆类型和方向限制
            if (grid.can_pass(*n, vehicle_type) and 
                grid.is_move_valid_by_direction(u.i, u.j, *n) and 
                n not in closed):
                heappush(open_, Node(n, u.g + 1, h(n, target)))
                closed[n] = (u.i, u.j)

        if step >= max_steps or (u.i, u.j) == target or len(open_) == 0:
            break

    next_node = target if target in closed else None
    path = []
    while next_node is not None:
        path.append(next_node)
        next_node = closed[next_node]

    return list(reversed(path))


def a_star(start, target, grid: GridMemory, max_steps=10000):
    """原始的A*算法，保持向后兼容"""
    return a_star_vehicle_aware(start, target, grid, vehicle_type='standard', max_steps=max_steps)


class AStarAgent:
    def __init__(self, seed=0, vehicle_type='standard'):
        self._moves = GridConfig().MOVES
        self._reverse_actions = {tuple(self._moves[i]): i for i in range(len(self._moves))}

        self._gm = None
        self._saved_xy = None
        self.vehicle_type = vehicle_type  # 车辆类型
        self.clear_state()
        self._rnd = np.random.default_rng(seed)

    def act(self, obs):
        xy, target_xy, obstacles, agents = obs['xy'], obs['target_xy'], obs['obstacles'], obs['agents']
        
        # 获取货物信息（如果观察中包含）
        stocks = obs.get('stocks', None)
        directions = obs.get('directions', None)


        if self._saved_xy is not None and h(self._saved_xy, xy) > 1:
            raise IndexError("Agent moved more than 1 step. Please, call clear_state method before new episode.")
        if self._saved_xy is not None and h(self._saved_xy, xy) == 0 and xy != target_xy:
            return self._rnd.integers(len(self._moves))
        
        # 更新网格内存，包括货物信息
        self._gm.update(*xy, obstacles, stocks, directions)
        
        # 使用车辆类型感知的A*算法
        path = a_star_vehicle_aware(xy, target_xy, self._gm, self.vehicle_type)
        
        if len(path) <= 1:
            action = 0
        else:
            (x, y), (tx, ty), *_ = path
            action = self._reverse_actions[tx - x, ty - y]

        self._saved_xy = xy
        return action

    def clear_state(self):
        self._saved_xy = None
        self._gm = GridMemory()


class BatchAStarAgent:
    def __init__(self, vehicle_types=None):
        """
        批量A*智能体
        :param vehicle_types: 车辆类型列表，如 ['small', 'standard', 'heavy']
                             如果为None，所有智能体都使用'standard'
        """
        self.astar_agents = {}
        self.vehicle_types = vehicle_types or []

    def act(self, observations):
        actions = []
        for idx, obs in enumerate(observations):
            if idx not in self.astar_agents:
                # 根据索引确定车辆类型
                if idx < len(self.vehicle_types):
                    vehicle_type = self.vehicle_types[idx]
                else:
                    vehicle_type = 'standard'  # 默认类型
                
                self.astar_agents[idx] = AStarAgent(vehicle_type=vehicle_type)
            actions.append(self.astar_agents[idx].act(obs))
        return actions

    def reset_states(self):
        self.astar_agents = {}
