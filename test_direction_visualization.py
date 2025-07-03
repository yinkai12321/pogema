#!/usr/bin/env python3
"""
测试方向指示器的显示效果
"""

def test_direction_visualization():
    """测试方向指示器的可视化"""
    print("=== 测试方向指示器可视化 ===")
    
    # 创建包含各种方向的测试地图
    grid = """
.AB.#..
--|....
..--%..
..||%..
#.|.#..
#.#.#ab""".strip()
    
    print("测试地图:")
    print(grid)
    print()
    print("地图说明:")
    print("- '.': 全方向移动（无特殊显示）")
    print("- '-': 左右移动（绿色水平条）")
    print("- '|': 上下移动（蓝色垂直条）")
    print("- '#': 障碍物（灰色方块）")
    print("- '%': 货物（橙色方块）")
    print("- 字母: 智能体起始位置和目标")
    print()
    
    from pogema import GridConfig, pogema_v0, BatchAStarAgent, AnimationMonitor, AnimationConfig
    import os
    
    # 创建配置
    grid_config = GridConfig(
        size=32, 
        num_agents=2, 
        obs_radius=3,
        seed=8, 
        on_target='finish',
        max_episode_steps=32, 
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
    print(directions)
    print()
    
    # 创建智能体
    agent = BatchAStarAgent(vehicle_types=['small', 'standard'])
    
    # 运行几步
    print("=== 运行仿真 ===")
    terminated = truncated = [False, False]
    step_count = 0
    
    while not all(terminated) and not all(truncated) and step_count < 15:
        actions = agent.act(obs)
        obs, _, terminated, truncated, _ = env.step(actions)
        step_count += 1
        
        if step_count % 5 == 0:
            print(f"已执行 {step_count} 步")
    
    print("仿真完成!")
    
    # 保存动画
    anim_folder = 'renders'
    if not os.path.exists(anim_folder):
        os.makedirs(anim_folder)
    
    # 保存不同类型的动画
    animations = [
        ('anim-directions-normal.svg', AnimationConfig()),
        ('anim-directions-static.svg', AnimationConfig(static=True)),
        ('anim-directions-ego-0.svg', AnimationConfig(egocentric_idx=0)),
        ('anim-directions-ego-0-static.svg', AnimationConfig(egocentric_idx=0, static=True)),
    ]
    
    for filename, config in animations:
        env.save_animation(f'{anim_folder}/{filename}', config)
        print(f"动画已保存到 {anim_folder}/{filename}")
    
    print()
    print("=== 视觉效果说明 ===")
    print("在生成的SVG动画中，您应该看到:")
    print("- 绿色水平条: 表示只能左右移动的位置 (-)")
    print("- 蓝色垂直条: 表示只能上下移动的位置 (|)")
    print("- 灰色方块: 障碍物 (#)")
    print("- 橙色方块: 货物 (%)")
    print("- 彩色圆圈: 智能体")
    print("- 空心圆圈: 目标位置")

if __name__ == "__main__":
    test_direction_visualization()
