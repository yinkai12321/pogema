#!/usr/bin/env python3
"""
演示方向限制箭头可视化的脚本
"""

from pogema import GridConfig, pogema_v0
from pogema.svg_animation.animation_wrapper import AnimationMonitor, AnimationConfig
from pogema.a_star_policy import BatchAStarAgent
import os

def demo_arrow_directions():
    """演示方向限制箭头可视化"""
    print("🎯 演示方向限制箭头可视化")
    
    # 创建包含方向限制的地图
    # . = 无限制, - = 左右, | = 上下
    grid_map = """
    ....-....
    ..|..|...
    ..|..|...
    ---.---..
    .........
    .||..||..
    .||..||..
    .........
    """.strip()
    
    print("地图布局:")
    print(grid_map)
    print("\n图例:")
    print("  . = 无方向限制 (全方向)")
    print("  - = 左右方向限制 (水平箭头)")
    print("  | = 上下方向限制 (垂直箭头)")
    
    # 创建环境配置
    grid_config = GridConfig(
        num_agents=2,
        size=32,
        obs_radius=5,
        seed=42,
        max_episode_steps=32,
        map=grid_map,
        on_target='finish'
    )
    
    # 创建环境
    env = pogema_v0(grid_config=grid_config)
    env = AnimationMonitor(env, AnimationConfig(save_every_idx_episode=None))
    
    # 重置环境
    obs, info = env.reset()
    
    # 创建A*智能体
    agent = BatchAStarAgent()
    
    # 运行几步
    step_count = 0
    terminated = [False] * grid_config.num_agents
    truncated = [False] * grid_config.num_agents
    
    while not all(terminated) and not all(truncated) and step_count < 20:
        actions = agent.act(obs)
        obs, rewards, terminated, truncated, info = env.step(actions)
        step_count += 1
        print(f"步骤 {step_count}: 动作 {actions}")
    
    # 确保渲染目录存在
    renders_dir = 'renders'
    if not os.path.exists(renders_dir):
        os.makedirs(renders_dir)
    
    # 保存动画
    static_file = f'{renders_dir}/demo-arrow-directions-static.svg'
    animated_file = f'{renders_dir}/demo-arrow-directions-animated.svg'
    
    # 保存静态版本（更容易查看箭头）
    env.save_animation(static_file, AnimationConfig(static=True))
    print(f"✅ 静态动画已保存到: {static_file}")
    
    # 保存动画版本
    env.save_animation(animated_file, AnimationConfig(static=False))
    print(f"✅ 动画已保存到: {animated_file}")
    
    # 检查SVG文件内容
    if os.path.exists(static_file):
        with open(static_file, 'r') as f:
            content = f.read()
            if 'polygon' in content:
                print("✅ SVG文件中包含polygon元素（箭头）")
            else:
                print("❌ SVG文件中未找到polygon元素")
    
    print("\n🎉 方向限制箭头可视化演示完成!")
    print("请打开生成的SVG文件查看箭头效果")

if __name__ == "__main__":
    demo_arrow_directions()
