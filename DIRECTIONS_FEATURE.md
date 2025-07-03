# Pogema 方向限制功能说明

## 概述
我们在 Pogema 环境中成功添加了地图方向限制功能，支持三种不同的移动方向约束：

## 方向类型
- **0**: 四个方向都可以走 (`.` 在地图中表示)
- **1**: 仅限左右方向移动 (`-` 在地图中表示)
- **2**: 仅限上下方向移动 (`|` 在地图中表示)

## 实现的功能

### 1. GridConfig 扩展
- 修改了 `str_map_to_list` 方法，解析地图字符串中的方向信息
- 支持 `-` 字符表示左右方向，`|` 字符表示上下方向
- 返回额外的方向矩阵

### 2. Grid 类扩展
- 添加了 `directions` 属性存储方向信息
- 实现了 `get_directions()` 方法获取方向矩阵
- 实现了 `get_directions_for_agent()` 方法获取智能体局部方向信息
- 实现了 `is_move_valid()` 方法检查移动是否符合方向限制

### 3. A* 智能体扩展
- 在 `GridMemory` 类中添加了 `_directions_memory` 存储方向信息
- 实现了 `get_direction_type()` 方法获取位置的方向类型
- 实现了 `is_move_valid_by_direction()` 方法检查移动的方向有效性
- 修改了 `a_star_vehicle_aware()` 算法，在路径规划时考虑方向限制

### 4. 环境集成
- 环境在重置时会解析地图的方向信息
- 智能体观察中包含方向信息
- A* 算法在路径规划时会自动考虑方向限制

## 使用示例

### 地图定义
```python
grid = """
.AB.#..
--|....
..--%..
..||%..
#.#.#..
#.#.#ab
""".strip()
```

在这个地图中：
- `.` 表示可以四个方向移动的自由空间
- `-` 表示只能左右移动的区域
- `|` 表示只能上下移动的区域
- `#` 表示障碍物
- `%` 表示货物位置
- 字母表示智能体起始位置和目标位置

### 创建环境
```python
from pogema import GridConfig, pogema_v0, BatchAStarAgent

grid_config = GridConfig(
    num_agents=2,
    obs_radius=3,
    on_target='finish',
    max_episode_steps=32,
    map=grid,
    observation_type="POMAPF"
)

env = pogema_v0(grid_config=grid_config)
agent = BatchAStarAgent(vehicle_types=['small', 'standard'])
```

### 运行仿真
```python
obs, info = env.reset()
terminated = truncated = [False, False]

while not all(terminated) and not all(truncated):
    actions = agent.act(obs)
    obs, _, terminated, truncated, _ = env.step(actions)
```

## 测试验证
我们创建了多个测试文件验证功能：

1. **test_directions.py**: 基本的方向解析测试
2. **test_pogema_directions.py**: 环境集成测试
3. **test_astar_directions.py**: A* 算法测试
4. **test_direction_constraints.py**: 方向限制详细测试

所有测试都通过，证明功能正常工作。

## 技术细节

### 方向限制逻辑
```python
def is_move_valid_by_direction(self, from_x, from_y, to_x, to_y):
    direction_type = self.get_direction_type(from_x, from_y)
    dx = to_x - from_x
    dy = to_y - from_y
    
    if abs(dx) + abs(dy) != 1:  # 必须是相邻移动
        return False
        
    if direction_type == 0:  # 全方向
        return True
    elif direction_type == 1:  # 左右方向
        return dy != 0 and dx == 0
    elif direction_type == 2:  # 上下方向
        return dx != 0 and dy == 0
    
    return False
```

### A* 算法集成
A* 算法在搜索路径时会检查每个移动是否符合方向限制：
```python
for n in [(u.i - 1, u.j), (u.i + 1, u.j), (u.i, u.j - 1), (u.i, u.j + 1)]:
    if (grid.can_pass(*n, vehicle_type) and 
        grid.is_move_valid_by_direction(u.i, u.j, *n) and 
        n not in closed):
        # 添加到搜索队列
```

## 兼容性
- 向后兼容：现有代码无需修改仍可正常运行
- 如果地图不包含方向字符，默认所有位置为全方向移动
- 支持与现有的车辆类型、货物系统等功能组合使用

## 性能影响
- 方向检查的计算复杂度为 O(1)
- 对 A* 算法的性能影响极小
- 内存开销：每个网格位置额外存储一个整数 (4 字节)
