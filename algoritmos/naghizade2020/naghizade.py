from algoritmos.naghizade2020.flipflop import flip_flop_exchange
from algoritmos.naghizade2020.treat_data import Segmented, Stop, SubSegment


def naghizade(trajectories: list[Segmented], pois: list[Stop], axis: float):
    anonymized = []

    for trajectory in trajectories:
        subtrajectories = get_sensitive_subtrajectory(trajectory)
        anonymized.append(flip_flop_exchange(trajectory, subtrajectories, pois, axis))


# TODO: arrumar essa função
def get_sensitive_subtrajectory(trajectory: Segmented) -> list[SubSegment]:
    init_index = None
    subtrajectories = []
    subtrajectory = []
    for i, segment in enumerate(trajectory.points):
        if isinstance(segment, Stop):
            priv_level = trajectory.privacy_settings[segment.semantic]
            # o segmento é sensível e precisa ser substituido
            if priv_level > segment.sensitivity:
                if subtrajectory:
                    subtrajectories.append(SubSegment(subtrajectory, init_index, i))
                subtrajectory = [segment]
                init_index = i
            # o segmento não é sensível e pode ser adicionado à subtrajetoria
            else:
                if subtrajectory:
                    subtrajectory.append(segment)

        elif subtrajectory:
            subtrajectory.append(segment)

    return subtrajectories
