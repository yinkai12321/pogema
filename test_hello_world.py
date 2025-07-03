from pogema import pogema_v0,AnimationMonitor
from pogema.grid import GridConfig


def test_basic_pogema_creation():
    """测试基本的 Pogema 环境创建"""
    config = GridConfig(num_agents=1, size=5, seed=42)
    env = pogema_v0(config)
    env = AnimationMonitor(env)
    obs, info = env.reset()

    # 运行几个步骤
    for step in range(100):
        actions = env.sample_actions()  # 随机动作
        obs, rewards, terminated, truncated, info = env.step(actions)
        if all(terminated) or all(truncated):
            break
    env.save_animation("tests/hello_world_animation.svg")

def main():
    """主函数，运行所有测试"""
    print("Running Hello World tests...")
    
    try:
        test_basic_pogema_creation()
        print("✓ test_basic_pogema_creation passed")
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        raise


if __name__ == "__main__":
    main()