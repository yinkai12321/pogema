import sys
from typing import Optional, Union
from pydantic import validator

from pogema.utils import CommonSettings

from typing_extensions import Literal


class GridConfig(CommonSettings, ):
    on_target: Literal['finish', 'nothing', 'restart'] = 'finish'
    seed: Optional[int] = None
    size: int = 8
    density: float = 0.3
    obs_radius: int = 5
    agents_xy: Optional[list] = None
    targets_xy: Optional[list] = None
    num_agents: Optional[int] = None
    possible_agents_xy: Optional[list] = None
    possible_targets_xy: Optional[list] = None
    collision_system: Literal['block_both', 'priority', 'soft'] = 'priority'
    persistent: bool = False
    observation_type: Literal['POMAPF', 'MAPF', 'default'] = 'default'
    map: Optional[Union[list, str]] = None

    map_name: Optional[str] = None

    integration: Literal['SampleFactory', 'PyMARL', 'rllib', 'gymnasium', 'PettingZoo'] = None
    max_episode_steps: int = 64
    auto_reset: Optional[bool] = None

    @validator('seed')
    def seed_initialization(cls, v):
        assert v is None or (0 <= v < sys.maxsize), "seed must be in [0, " + str(sys.maxsize) + ']'
        return v

    @validator('size')
    def size_restrictions(cls, v):
        assert 2 <= v <= 4096, "size must be in [2, 4096]"
        return v

    @validator('density')
    def density_restrictions(cls, v):
        assert 0.0 <= v <= 1, "density must be in [0, 1]"
        return v

    @validator('agents_xy')
    def agents_xy_validation(cls, v, values):
        if v is not None:
            cls.check_positions(v, values['size'])
        return v

    @validator('targets_xy')
    def targets_xy_validation(cls, v, values):
        if v is not None:
            cls.check_positions(v, values['size'])
        return v

    @validator('num_agents', always=True)
    def num_agents_must_be_positive(cls, v, values):
        if v is None:
            if values['agents_xy']:
                v = len(values['agents_xy'])
            else:
                v = 1
        assert 1 <= v <= 10000000, "num_agents must be in [1, 10000000]"
        return v

    @validator('obs_radius')
    def obs_radius_must_be_positive(cls, v):
        assert 1 <= v <= 128, "obs_radius must be in [1, 128]"
        return v

    @validator('map', always=True)
    def map_validation(cls, v, values):
        if v is None:
            return None
        if isinstance(v, str):
            v, stocks, agents_xy, targets_xy, possible_agents_xy, possible_targets_xy = cls.str_map_to_list(v, values['FREE'],
                                                                                                    values['OBSTACLE'])
            if agents_xy and targets_xy and values.get('agents_xy') is not None and values.get(
                    'targets_xy') is not None:
                raise KeyError("""Can't create task. Please provide agents_xy and targets_xy only once.
                Either with parameters or with a map.""")
            if (agents_xy or targets_xy) and (possible_agents_xy or possible_targets_xy):
                raise KeyError("""Can't create task. Mark either possible locations or precise ones.""")
            elif agents_xy and targets_xy:
                values['agents_xy'] = agents_xy
                values['targets_xy'] = targets_xy
                values['num_agents'] = len(agents_xy)
            elif (values.get('agents_xy') is None or values.get(
                    'targets_xy') is None) and possible_agents_xy and possible_targets_xy:
                values['possible_agents_xy'] = possible_agents_xy
                values['possible_targets_xy'] = possible_targets_xy
        size = len(v)
        area = 0
        for line in v:
            size = max(size, len(line))
            area += len(line)
        values['size'] = size
        values['density'] = sum([sum(line) for line in v]) / area

        return v, stocks

    @validator('possible_agents_xy')
    def possible_agents_xy_validation(cls, v):
        return v

    @validator('possible_targets_xy')
    def possible_targets_xy_validation(cls, v):
        return v

    @staticmethod
    def check_positions(v, size):
        for position in v:
            x, y = position
            if not (0 <= x < size and 0 <= y < size):
                raise IndexError("Position is out of bounds!")

    @staticmethod
    def str_map_to_list(str_map, free, obstacle):
        obstacles = []
        stocks = []  # 货物
        agents = {}
        targets = {}
        possible_agents_xy = []
        possible_targets_xy = []
        special_chars = {'@', '$', '!', '%'}  # 添加 % 符号

        # 检查地图中是否有明确的智能体定义（字母）
        has_explicit_agents = any(c.isalpha() for c in str_map)

        for row_idx, line in enumerate(str_map.split()):
            obstacle_row = []
            stock_row = []  # 新增：货物行
            
            for col_idx, char in enumerate(line):
                position = (row_idx, col_idx)

                if char == '.':
                    obstacle_row.append(free)
                    stock_row.append(free)  # 自由区域没有货物
                    possible_agents_xy.append(position)
                    possible_targets_xy.append(position)
                elif char == '#':
                    obstacle_row.append(obstacle)
                    stock_row.append(free)  # 障碍物位置没有货物
                elif char == '%':  # 新增：货物符号处理
                    obstacle_row.append(free)  # 货物位置是自由通行的
                    stock_row.append(obstacle)  # 标记为有货物（使用obstacle值表示存在）
                    possible_agents_xy.append(position)  # 智能体可以到达货物位置
                    possible_targets_xy.append(position)
                elif char in special_chars:
                    obstacle_row.append(free)
                    stock_row.append(free)  # 特殊字符位置没有货物
                    if char == '@':
                        possible_agents_xy.append(position)
                    elif char == '$':
                        possible_targets_xy.append(position)
                elif 'A' <= char <= 'Z':
                    targets[char.lower()] = position
                    obstacle_row.append(free)
                    stock_row.append(free)  # 目标位置没有货物
                    possible_agents_xy.append(position)
                    possible_targets_xy.append(position)
                elif 'a' <= char <= 'z':
                    agents[char.lower()] = position
                    obstacle_row.append(free)
                    stock_row.append(free)  # 智能体起始位置没有货物
                    possible_agents_xy.append(position)
                    possible_targets_xy.append(position)
                else:
                    raise KeyError(f"Unsupported symbol '{char}' at line {row_idx}")

            if obstacle_row:
                assert len(obstacles[-1]) == len(obstacle_row) if obstacles else True, f"Wrong string size for row {row_idx};"
                obstacles.append(obstacle_row)
                stocks.append(stock_row)  # 添加货物行

        agents_xy = [[x, y] for _, (x, y) in sorted(agents.items())]
        targets_xy = [[x, y] for _, (x, y) in sorted(targets.items())]

        assert len(targets_xy) == len(agents_xy), "Mismatch in number of agents and targets."

        if has_explicit_agents or not any(char in special_chars for char in str_map):
            possible_agents_xy, possible_targets_xy = None, None

        return obstacles, stocks, agents_xy, targets_xy, possible_agents_xy, possible_targets_xy
