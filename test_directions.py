#!/usr/bin/env python3
"""
测试方向功能的简单脚本
"""

def test_directions():
    """测试方向功能"""
    print("=== 测试方向功能 ===")
    
    # 创建测试地图
    grid = """
.AB.#..
--|....
..--%..
..||%..
#.#.#..
#.#.#ab
""".strip()
    
    print("测试地图:")
    print(grid)
    print()
    
    # 直接测试GridConfig的str_map_to_list方法
    from pogema.grid_config import GridConfig
    
    try:
        result = GridConfig.str_map_to_list(grid, 0, 1)
        print(f"str_map_to_list返回值数量: {len(result)}")
        
        obstacles, stocks, directions, agents_xy, targets_xy, possible_agents_xy, possible_targets_xy = result
        
        print("障碍物矩阵:")
        for row in obstacles:
            print(row)
        print()
        
        print("货物矩阵:")
        for row in stocks:
            print(row)
        print()
        
        print("方向矩阵:")
        for row in directions:
            print(row)
        print()
        
        print("智能体位置:", agents_xy)
        print("目标位置:", targets_xy)
        print()
        
        # 方向说明
        print("方向说明:")
        print("0: 四个方向都可以走 ('.')")
        print("1: 左右方向 ('-')")
        print("2: 上下方向 ('|')")
        print()
        
        # 手动测试移动有效性逻辑
        print("=== 测试移动有效性逻辑 ===")
        
        def is_move_valid(directions, from_pos, to_pos):
            """简单的移动有效性检查"""
            if not (0 <= from_pos[0] < len(directions) and 
                    0 <= from_pos[1] < len(directions[0])):
                return False
                
            direction_type = directions[from_pos[0]][from_pos[1]]
            
            dx = to_pos[0] - from_pos[0]
            dy = to_pos[1] - from_pos[1]
            
            # 检查是否为相邻移动
            if abs(dx) + abs(dy) != 1:
                return False
                
            if direction_type == 0:  # 全方向
                return True
            elif direction_type == 1:  # 左右
                return dx == 0 and dy != 0
            elif direction_type == 2:  # 上下
                return dy == 0 and dx != 0
            
            return False
        
        # 测试点 (1, 1) - 左右方向
        from_pos = [1, 1]
        print(f"从位置 {from_pos} (方向类型: {directions[1][1]}) 测试移动:")
        
        # 测试四个方向的移动
        test_moves = [
            ([0, 1], "上"),
            ([2, 1], "下"),
            ([1, 0], "左"),
            ([1, 2], "右")
        ]
        
        for to_pos, direction in test_moves:
            if (0 <= to_pos[0] < len(directions) and 
                0 <= to_pos[1] < len(directions[0])):
                valid = is_move_valid(directions, from_pos, to_pos)
                print(f"  向{direction}移动到 {to_pos}: {'有效' if valid else '无效'}")
        print()
        
        # 测试点 (3, 2) - 上下方向
        from_pos = [3, 2]
        print(f"从位置 {from_pos} (方向类型: {directions[3][2]}) 测试移动:")
        
        for to_pos, direction in test_moves:
            to_pos_adjusted = [from_pos[0] + (to_pos[0] - from_pos[0]), from_pos[1] + (to_pos[1] - from_pos[1])]
            if (0 <= to_pos_adjusted[0] < len(directions) and 
                0 <= to_pos_adjusted[1] < len(directions[0])):
                valid = is_move_valid(directions, from_pos, to_pos_adjusted)
                print(f"  向{direction}移动到 {to_pos_adjusted}: {'有效' if valid else '无效'}")
        print()
        
    except Exception as e:
        print(f"发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_directions()
