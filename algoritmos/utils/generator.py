import random

from algoritmos.utils.semantic import PoiCategory
from algoritmos.utils.trajetory import Trajectory


def generate_settings(trajectories: dict[str, Trajectory]) -> \
        dict[str, tuple[Trajectory, dict[PoiCategory]]]:
    new_trajectories = {}

    for user_id in trajectories:
        trajectory = trajectories[user_id]
        settings = random_privacy_settings()
        new_trajectories[user_id] = (trajectory, settings)

    return new_trajectories


def random_privacy_settings() -> dict[PoiCategory, float]:
    settings = {}
    for category in PoiCategory:
        settings[category] = random.randint(1, 10) / 10

    return settings
