#!/usr/bin/env python3
"""
创建一个专门展示方向指示器的简单地图
"""

def create_direction_showcase():
    """创建方向指示器展示"""
    print("=== 方向指示器展示 ===")
    
    # 创建一个专门展示方向的地图
    grid = """
....-....
....-.|||
--|..-..||
--|..-..||
....-.|||
....-....
||||.||||
||||.||||
---------
......Ab.""".strip()
    
    print("方向展示地图:")
    print(grid)
    print()
    
    from pogema import GridConfig, pogema_v0, AnimationMonitor, AnimationConfig
    import os
    
    # 创建配置
    grid_config = GridConfig(
        size=32, 
        num_agents=1, 
        obs_radius=5,  # 大观察半径，看到整个地图
        seed=42, 
        on_target='finish',
        max_episode_steps=50, 
        density=0.1, 
        map=grid, 
        observation_type="POMAPF"
    )
    
    # 创建环境
    env = pogema_v0(grid_config=grid_config)
    env = AnimationMonitor(env, AnimationConfig(save_every_idx_episode=None))
    
    # 重置环境
    obs, info = env.reset()
    print("环境重置成功")
    
    # 获取网格信息
    grid_obj = env.grid
    
    print("方向矩阵:")
    directions = grid_obj.get_directions(ignore_borders=True)
    for row in directions:
        print(''.join([str(x) for x in row]))
    print()
    
    print("方向类型统计:")
    # 手动统计
    direction_counts = {0: 0, 1: 0, 2: 0}
    for row in directions:
        for val in row:
            direction_counts[val] += 1
    
    for direction_type, count in direction_counts.items():
        if direction_type == 0:
            print(f"  全方向 (0): {count} 个位置")
        elif direction_type == 1:
            print(f"  左右 (1): {count} 个位置")
        elif direction_type == 2:
            print(f"  上下 (2): {count} 个位置")
    print()
    
    # 保存静态动画以查看效果
    anim_folder = 'renders'
    if not os.path.exists(anim_folder):
        os.makedirs(anim_folder)
    
    # 只保存静态版本，方便查看方向指示器
    env.save_animation(f'{anim_folder}/direction-showcase.svg', 
                       AnimationConfig(static=True, show_agents=True))
    
    print(f"方向展示动画已保存到 {anim_folder}/direction-showcase.svg")
    print()
    print("=== 颜色说明 ===")
    print("- 绿色水平条 (─): 只能左右移动")
    print("- 蓝色垂直条 (│): 只能上下移动")
    print("- 无额外标记: 可以四个方向移动")
    print("- 彩色圆圈: 智能体起始位置")
    print("- 空心圆圈: 目标位置")

if __name__ == "__main__":
    create_direction_showcase()
