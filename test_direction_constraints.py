#!/usr/bin/env python3
"""
测试方向限制的简单示例
"""

def test_direction_constraints():
    """测试方向限制功能"""
    print("=== 测试方向限制 ===")
    
    from pogema.a_star_policy import GridMemory
    import numpy as np
    
    # 创建一个简单的测试场景
    print("创建测试场景:")
    print("- 障碍物矩阵 (5x5):")
    obstacles = np.array([
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0]
    ], dtype=np.float32)
    print(obstacles)
    print()
    
    print("- 方向矩阵 (5x5):")
    directions = np.array([
        [0, 1, 0, 2, 0],  # 0=全向, 1=左右, 2=上下
        [1, 1, 0, 2, 0],
        [0, 0, 0, 2, 0],
        [1, 1, 0, 2, 0],
        [0, 1, 0, 2, 0]
    ], dtype=np.int32)
    print(directions)
    print()
    
    # 创建GridMemory并更新
    gm = GridMemory(start_r=32)
    gm.update(0, 0, obstacles, directions=directions)
    
    # 测试方向限制
    print("=== 测试方向限制 ===")
    
    test_cases = [
        # 从 (0,1) 位置测试（实际是方向类型2=上下）
        {"from": (0, 1), "to": (-1, 1), "expected": True, "desc": "上下位置向上移动"},
        {"from": (0, 1), "to": (1, 1), "expected": True, "desc": "上下位置向下移动"},
        {"from": (0, 1), "to": (0, 0), "expected": False, "desc": "上下位置向左移动"},
        {"from": (0, 1), "to": (0, 2), "expected": False, "desc": "上下位置向右移动"},
        
        # 从 (-1,-1) 位置测试（实际是方向类型1=左右）
        {"from": (-1, -1), "to": (-1, -2), "expected": True, "desc": "左右位置向左移动"},
        {"from": (-1, -1), "to": (-1, 0), "expected": True, "desc": "左右位置向右移动"},
        {"from": (-1, -1), "to": (-2, -1), "expected": False, "desc": "左右位置向上移动"},
        {"from": (-1, -1), "to": (0, -1), "expected": False, "desc": "左右位置向下移动"},
        
        # 从 (0,0) 全方向位置测试
        {"from": (0, 0), "to": (0, 1), "expected": True, "desc": "全方向位置向右移动"},
        {"from": (0, 0), "to": (1, 0), "expected": True, "desc": "全方向位置向下移动"},
        {"from": (0, 0), "to": (0, -1), "expected": True, "desc": "全方向位置向左移动"},
        {"from": (0, 0), "to": (-1, 0), "expected": True, "desc": "全方向位置向上移动"},
    ]
    
    # 首先显示所有位置的方向类型
    print("所有位置的方向类型:")
    for i in range(5):
        for j in range(5):
            direction_type = gm.get_direction_type(i-2, j-2)  # GridMemory中心偏移
            print(f"({i-2},{j-2}):{direction_type}", end=" ")
        print()
    print()
    
    for case in test_cases:
        from_pos = case["from"]
        to_pos = case["to"]
        expected = case["expected"]
        desc = case["desc"]
        
        # 先检查方向类型
        direction_type = gm.get_direction_type(*from_pos)
        print(f"位置 {from_pos} 的方向类型: {direction_type}")
        
        result = gm.is_move_valid_by_direction(*from_pos, *to_pos)
        status = "✓" if result == expected else "✗"
        print(f"{status} {desc}: {result} (期望: {expected})")
        print()
    
    print()
    print("=== 使用A*算法测试路径规划 ===")
    
    from pogema.a_star_policy import a_star_vehicle_aware
    
    # 测试从左右限制位置的路径规划
    start = (0, 1)  # 左右限制位置
    target = (0, 4)  # 目标位置
    
    print(f"从 {start} 到 {target} 的路径规划:")
    path = a_star_vehicle_aware(start, target, gm, vehicle_type='standard')
    print(f"路径: {path}")
    
    # 验证路径中的每一步都符合方向限制
    valid_path = True
    for i in range(len(path) - 1):
        from_pos = path[i]
        to_pos = path[i + 1]
        if not gm.is_move_valid_by_direction(*from_pos, *to_pos):
            print(f"✗ 无效移动: {from_pos} -> {to_pos}")
            valid_path = False
    
    if valid_path:
        print("✓ 路径中的所有移动都符合方向限制")
    else:
        print("✗ 路径中存在不符合方向限制的移动")

if __name__ == "__main__":
    test_direction_constraints()
