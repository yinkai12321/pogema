from typing import Union, Optional

from gymnasium import Wrapper

from pogema import GridConfig
from pogema.envs import _make_pogema
from pogema.integrations.pettingzoo import parallel_env
from pogema.integrations.pymarl import PyMarlPogema
from pogema.integrations.sample_factory import AutoResetWrapper, IsMultiAgentWrapper, MetricsForwardingWrapper


def _make_sample_factory_integration(grid_config):
    env = _make_pogema(grid_config)
    env = MetricsForwardingWrapper(env)
    env = IsMultiAgentWrapper(env)
    if grid_config.auto_reset is None or grid_config.auto_reset:
        env = AutoResetWrapper(env)
    return env


def _make_py_marl_integration(grid_config, *_, **__):
    return PyMarlPogema(grid_config)


class SingleAgentWrapper(Wrapper):

    def step(self, action):
        observations, rewards, terminated, truncated, infos = self.env.step(
            [action] + [self.env.action_space.sample() for _ in range(self.get_num_agents() - 1)])
        return observations[0], rewards[0], terminated[0], truncated[0], infos[0]

    def reset(self, seed: Optional[int] = None, return_info: bool = True, options: Optional[dict] = None, ):
        observations, infos = self.env.reset()
        if return_info:
            return observations[0], infos[0]
        else:
            return observations[0]


def make_single_agent_gym(grid_config: Union[GridConfig, dict] = GridConfig()):
    env = _make_pogema(grid_config)
    env = SingleAgentWrapper(env)

    return env


def make_pogema(grid_config: Union[GridConfig, dict] = GridConfig(), *args, **kwargs):
    if isinstance(grid_config, dict):
        grid_config = GridConfig(**grid_config)

    if grid_config.integration != 'SampleFactory' and grid_config.auto_reset:
        raise KeyError(f"{grid_config.integration} does not support auto_reset")

    if grid_config.integration is None:
        return _make_pogema(grid_config)
    elif grid_config.integration == 'SampleFactory':
        return _make_sample_factory_integration(grid_config)
    elif grid_config.integration == 'PyMARL':
        return _make_py_marl_integration(grid_config, *args, **kwargs)
    elif grid_config.integration == 'rllib':
        raise NotImplementedError('Please use PettingZoo integration for rllib')
    elif grid_config.integration == 'PettingZoo':
        return parallel_env(grid_config)
    elif grid_config.integration == 'gymnasium':
        return make_single_agent_gym(grid_config)

    raise KeyError(grid_config.integration)


pogema_v0 = make_pogema
