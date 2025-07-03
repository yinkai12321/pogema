#!/usr/bin/env python3
"""
测试支持方向的A*算法
"""

def test_astar_with_directions():
    """测试A*算法对方向限制的支持"""
    print("=== 测试支持方向的A*算法 ===")
    
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
    
    from pogema import GridConfig, pogema_v0, BatchAStarAgent, AnimationMonitor, AnimationConfig
    
    # 创建配置
    grid_config = GridConfig(
        size=32, 
        num_agents=2, 
        obs_radius=3,  # 增大观察半径以便更好地测试
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
    print("网格对象创建成功")
    
    print("方向矩阵:")
    directions = grid_obj.get_directions(ignore_borders=True)
    print(directions)
    print()
    
    # 创建支持不同车辆类型的智能体
    agent = BatchAStarAgent(vehicle_types=['small', 'standard'])
    
    # 运行一些步骤
    print("=== 运行仿真 ===")
    terminated = truncated = [False, False]
    step_count = 0
    
    while not all(terminated) and not all(truncated) and step_count < 20:
        print(f"步骤 {step_count + 1}:")
        
        # 显示当前智能体位置
        for i, ob in enumerate(obs):
            print(f"  智能体 {i}: 位置 {ob['xy']}, 目标 {ob['target_xy']}")
        
        # 智能体决策
        actions = agent.act(obs)
        print(f"  动作: {actions}")
        
        # 执行动作
        obs, _, terminated, truncated, _ = env.step(actions)
        step_count += 1
        print()
    
    print("仿真完成!")
    
    # 保存动画
    import os
    anim_folder = 'renders'
    if not os.path.exists(anim_folder):
        os.makedirs(anim_folder)
    
    env.save_animation(f'{anim_folder}/anim-directions-test.svg')
    print(f"动画已保存到 {anim_folder}/anim-directions-test.svg")

if __name__ == "__main__":
    test_astar_with_directions()
