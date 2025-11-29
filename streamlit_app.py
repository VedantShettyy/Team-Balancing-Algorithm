import streamlit as st
from typing import List
from matchmaker import Player, optimize_teams, VAL_ROLES


# ----- Helper to build default players -----
def get_default_players() -> List[Player]:
    # fairness_score is left as the default (0.0) from the dataclass
    return [
        Player(id=1,  skill=1900, role="duelist",   party_id=1),
        Player(id=2,  skill=1750, role="initiator", party_id=1),
        Player(id=3,  skill=1600, role="sentinel"),
        Player(id=4,  skill=1500, role="controller"),
        Player(id=5,  skill=2100, role="duelist"),
        Player(id=6,  skill=1800, role="duelist"),
        Player(id=7,  skill=1700, role="controller"),
        Player(id=8,  skill=1650, role="initiator"),
        Player(id=9,  skill=1400, role="sentinel"),
        Player(id=10, skill=1550, role="sentinel"),
    ]


# ----- Streamlit UI -----
st.set_page_config(
    page_title="Valorant Matchmaker",
    page_icon="🎮",
    layout="wide",
)

st.title("🎮 Valorant 5v5 Matchmaker")
st.write("Enter your stack’s players, roles and parties, then generate balanced teams.")

# We keep iterations/seed as backend constants – not exposed in UI
DEFAULT_ITERATIONS = 5000
DEFAULT_SEED = 42
NUM_TEAMS = 2  # Valorant: 2 teams

st.markdown("### Player Pool")

# Keep players in session state so edits persist on rerun
if "players" not in st.session_state:
    st.session_state.players = get_default_players()

players = st.session_state.players

# Table header
cols = st.columns([1, 2, 2, 2])
with cols[0]:
    st.markdown("**ID**")
with cols[1]:
    st.markdown("**Skill (MMR / rank score)**")
with cols[2]:
    st.markdown("**Role**")
with cols[3]:
    st.markdown("**Party ID (optional)**")

# Editable rows
for p in players:
    c0, c1, c2, c3 = st.columns([1, 2, 2, 2])

    with c0:
        st.text(p.id)

    with c1:
        p.skill = c1.number_input(
            f"skill_{p.id}",
            value=float(p.skill),
            step=50.0,
            key=f"skill_{p.id}",
        )

    with c2:
        p.role = c2.selectbox(
            f"role_{p.id}",
            options=VAL_ROLES,
            index=VAL_ROLES.index(p.role) if p.role in VAL_ROLES else 0,
            key=f"role_{p.id}",
        )

    with c3:
        party_val = c3.text_input(
            f"party_{p.id}",
            value="" if p.party_id is None else str(p.party_id),
            key=f"party_{p.id}",
            placeholder="e.g. 1, 2, 3…",
        )
        p.party_id = int(party_val) if party_val.strip() != "" else None

st.markdown("---")

if st.button("Generate Balanced Teams"):
    with st.spinner("Optimizing teams…"):
        teams, best_cost = optimize_teams(
            players=players,
            iterations=DEFAULT_ITERATIONS,
            num_teams=NUM_TEAMS,
            seed=DEFAULT_SEED,
        )

    st.success(f"Final match quality score: **{best_cost:.2f}** (lower is better)")

    team_cols = st.columns(NUM_TEAMS)
    for t_idx, team in enumerate(teams):
        with team_cols[t_idx]:
            st.markdown(f"### Team {t_idx + 1}")
            for p in team:
                st.markdown(
                    f"- **Player {p.id}** | role `{p.role}` | "
                    f"skill {p.skill:.0f} | party {p.party_id}"
                )
else:
    st.info("Adjust players above and click **Generate Balanced Teams**.")