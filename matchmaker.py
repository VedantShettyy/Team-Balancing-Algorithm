from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import random

VAL_ROLES = ["duelist", "controller", "initiator", "sentinel"]

VAL_REQ = {
    "duelist": (1, 2),
    "controller": (1, 1),
    "initiator": (1, 2),
    "sentinel": (1, 2),
}


@dataclass
class Player:
    id: int
    skill: float
    role: str
    party_id: Optional[int] = None
    fairness_score: float = 0.0

def compute_team_stats(teams: List[List[Player]]):
    avg_skill = []
    role_counts_list = []

    for team in teams:
        if team:
            avg_skill.append(sum(p.skill for p in team) / len(team))
        else:
            avg_skill.append(0)

        counts = {}
        for p in team:
            counts[p.role] = counts.get(p.role, 0) + 1
        role_counts_list.append(counts)

    return avg_skill, role_counts_list


def skill_imbalance(avg_skill: List[float]) -> float:
    return max(avg_skill) - min(avg_skill) if avg_skill else 0.0


def valorant_role_penalty(role_counts_list: List[Dict[str, int]]) -> float:
    penalty = 0.0

    for counts in role_counts_list:
        for role, (min_req, max_req) in VAL_REQ.items():
            have = counts.get(role, 0)

            if have < min_req:
                penalty += (min_req - have) * 20.0

            if have > max_req:
                penalty += (have - max_req) * 10.0

    return penalty


def party_penalty(teams: List[List[Player]]) -> float:
    party_map = {}

    for t_idx, team in enumerate(teams):
        for p in team:
            if p.party_id is None:
                continue
            party_map.setdefault(p.party_id, set()).add(t_idx)

    penalty = 0.0
    for pid, team_set in party_map.items():
        if len(team_set) > 1:
            penalty += (len(team_set) - 1) * 25.0

    return penalty


def fairness_penalty(teams: List[List[Player]], avg_skill: List[float]) -> float:
    overall_avg = sum(avg_skill) / len(avg_skill)
    penalty = 0.0

    for t_idx, team in enumerate(teams):
        diff = avg_skill[t_idx] - overall_avg
        for p in team:
            penalty += abs(p.fairness_score * diff) * 1.0

    return penalty


def total_cost(teams: List[List[Player]]) -> float:
    avg_skill, role_counts = compute_team_stats(teams)

    return (
        skill_imbalance(avg_skill) * 1.0 +
        valorant_role_penalty(role_counts) * 1.0 +
        party_penalty(teams) * 1.0 +
        fairness_penalty(teams, avg_skill) * 0.7
    )

def initial_assign(players: List[Player], num_teams: int = 2):
    players_sorted = sorted(players, key=lambda p: p.skill, reverse=True)
    teams = [[] for _ in range(num_teams)]

    idx = 0
    direction = 1

    for p in players_sorted:
        teams[idx].append(p)
        idx += direction

        if idx == num_teams:
            idx = num_teams - 1
            direction = -1
        elif idx < 0:
            idx = 0
            direction = 1

    return teams

def optimize_teams(
    players: List[Player],
    iterations: int = 5000,
    num_teams: int = 2,
    seed: int = 42,
):
    random.seed(seed)

    teams = initial_assign(players, num_teams)
    best_cost = total_cost(teams)

    for _ in range(iterations):
        t1, t2 = random.sample(range(num_teams), 2)

        if not teams[t1] or not teams[t2]:
            continue

        i = random.randrange(len(teams[t1]))
        j = random.randrange(len(teams[t2]))

        teams[t1][i], teams[t2][j] = teams[t2][j], teams[t1][i]

        new_cost = total_cost(teams)

        if new_cost <= best_cost:
            best_cost = new_cost
        else:
            teams[t1][i], teams[t2][j] = teams[t2][j], teams[t1][i]

    return teams, best_cost
