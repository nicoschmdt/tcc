# Algorithm 4, Pag 6
from algoritmos.zhang2015.zhang import ZhangTrajectory


def get_groups(trajectories: list[ZhangTrajectory], alpha: float, k: int) -> list[list[ZhangTrajectory]]:
    groups = []
    not_grouped = [traj for traj in trajectories]
    for i, trajectory in enumerate(trajectories):
        if trajectory not in not_grouped:
            continue

        group = []
        for traj in trajectories[i:]:
            if trajectory.similarity(traj) == 1:
                not_grouped.remove(traj)
                group.append(traj)

        if group:
            not_grouped.remove(trajectory)
            groups.append(group)

    for trajectory in not_grouped:
        for group in groups:
            if trajectory.similarity_group(group) >= alpha:
                group.append(trajectory)
                break

    anonymized = []
    for group in groups:
        if len(group) >= k:
            anonymized.append(group)

    return anonymized
