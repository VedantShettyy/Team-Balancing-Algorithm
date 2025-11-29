from matchmaker import Player, optimize_teams

players = [
    Player(id=1,  skill=1900, role="duelist",    party_id=1),
    Player(id=2,  skill=1750, role="initiator",  party_id=1),
    Player(id=3,  skill=1600, role="sentinel"),
    Player(id=4,  skill=1500, role="controller"),
    Player(id=5,  skill=2100, role="duelist"),

    Player(id=6,  skill=1800, role="duelist"),
    Player(id=7,  skill=1700, role="controller"),
    Player(id=8,  skill=1650, role="initiator"),
    Player(id=9,  skill=1400, role="sentinel"),
    Player(id=10, skill=1550, role="sentinel"),
]

teams, cost = optimize_teams(players, iterations=5000)

print(f"\nFinal Cost = {cost}\n")

for t_idx, team in enumerate(teams):
    print(f"TEAM {t_idx + 1}")
    for p in team:
        print(f"  Player {p.id} | role={p.role} | skill={p.skill} | party={p.party_id}")
    print()
