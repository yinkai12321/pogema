#!/usr/bin/env python3
"""
测试与Pogema环境集成的方向功能
"""

def test_pogema_with_directions():
    """测试Pogema环境中的方向功能"""
    print("=== 测试Pogema环境中的方向功能 ===")
    
    # 创建测试地图
    grid = """
.AB.#..
--|....
..--%..
..||%..
#.#.#..
#.#.#ab""".strip()
    
    print("测试地图:")
    print(grid)
    print()
    
    from pogema import GridConfig, pogema_v0
    
    # 创建配置
    grid_config = GridConfig(
        size=32, 
        num_agents=2, 
        obs_radius=2, 
        seed=8, 
        on_target='finish',
        max_episode_steps=16, 
        density=0.1, 
        map=grid, 
        observation_type="POMAPF"
    )
    
    # 创建环境
    env = pogema_v0(grid_config=grid_config)
    
    # 重置环境
    obs, info = env.reset()
    print("环境重置成功")
    
    # 获取网格信息
    grid_obj = env.grid
    print("网格对象创建成功")
    
    print("障碍物矩阵:")
    obstacles = grid_obj.get_obstacles(ignore_borders=True)
    print(obstacles)
    print()
    
    print("货物矩阵:")
    stocks = grid_obj.get_stocks(ignore_borders=True)
    print(stocks)
    print()
    
    print("方向矩阵:")
    directions = grid_obj.get_directions(ignore_borders=True)
    print(directions)
    print()
    
    # 方向说明
    print("方向说明:")
    print("0: 四个方向都可以走 ('.')")
    print("1: 左右方向 ('-')")
    print("2: 上下方向 ('|')")
    print()
    
    # 测试移动有效性
    print("=== 测试移动有效性 ===")
    
    # 测试点 (1, 1) - 左右方向
    from_pos = [1, 1]
    print(f"从位置 {from_pos} (方向类型: {directions[1, 1]}) 测试移动:")
    
    # 测试四个方向的移动
    test_moves = [
        ([0, 1], "上"),
        ([2, 1], "下"),
        ([1, 0], "左"),
        ([1, 2], "右")
    ]
    
    for to_pos, direction in test_moves:
        valid = grid_obj.is_move_valid(from_pos, to_pos)
        print(f"  向{direction}移动到 {to_pos}: {'有效' if valid else '无效'}")
    print()
    
    # 测试点 (3, 2) - 上下方向
    from_pos = [3, 2]
    print(f"从位置 {from_pos} (方向类型: {directions[3, 2]}) 测试移动:")
    
    for to_pos, direction in test_moves:
        to_pos_adjusted = [from_pos[0] + (to_pos[0] - 1), from_pos[1] + (to_pos[1] - 1)]
        if (0 <= to_pos_adjusted[0] < directions.shape[0] and 
            0 <= to_pos_adjusted[1] < directions.shape[1]):
            valid = grid_obj.is_move_valid(from_pos, to_pos_adjusted)
            print(f"  向{direction}移动到 {to_pos_adjusted}: {'有效' if valid else '无效'}")
    print()
    
    # 测试点 (0, 0) - 全方向
    from_pos = [0, 0]
    print(f"从位置 {from_pos} (方向类型: {directions[0, 0]}) 测试移动:")
    
    for to_pos, direction in test_moves:
        to_pos_adjusted = [from_pos[0] + (to_pos[0] - 1), from_pos[1] + (to_pos[1] - 1)]
        if (0 <= to_pos_adjusted[0] < directions.shape[0] and 
            0 <= to_pos_adjusted[1] < directions.shape[1]):
            valid = grid_obj.is_move_valid(from_pos, to_pos_adjusted)
            print(f"  向{direction}移动到 {to_pos_adjusted}: {'有效' if valid else '无效'}")
    print()

if __name__ == "__main__":
    test_pogema_with_directions()
