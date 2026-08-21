import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="PMGO S1 Dashboard", layout="wide", page_icon="🎮")

# Load data
df = pd.read_csv("data/team_standings_clean.csv")

st.title("  PMGO 2026 Season 1 — Grand Finals Dashboard")
st.caption("Jakarta, Indonesia | June 2–7, 2026")

st.divider()

# --- Stat cards ---
col1, col2, col3, col4 = st.columns(4)
col1.metric(" Teams", len(df))
col2.metric(" Champion", df.loc[df['Rank'] == 1, 'Participant'].values[0])
col3.metric(" Total Games", 12)
col4.metric(" Top Score", int(df['Total Points'].max()))

st.divider()

# --- Bar chart: Total Points by team ---
fig = px.bar(
    df.sort_values("Total Points", ascending=True),
    x="Total Points",
    y="Participant",
    orientation="h",
    title="Total Points by Team",
    color="Total Points",
    color_continuous_scale="Oranges",
    text="Total Points"
)
fig.update_traces(textposition="outside")
fig.update_layout(showlegend=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
st.plotly_chart(fig, use_container_width=True)

# --- Placement vs Kill points ---
fig2 = px.bar(
    df.sort_values("Total Points", ascending=False),
    x="Participant",
    y=["Total Placement Points", "Total Kill Points"],
    title="Placement Points vs Kill Points",
    barmode="stack",
    color_discrete_map={
        "Total Placement Points": "#FF8700",
        "Total Kill Points": "#00C2CB"
    }
)
fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", legend_title_text="")
st.plotly_chart(fig2, use_container_width=True)

# --- Standings table ---
st.subheader(" Full Standings")
st.dataframe(
    df[['Rank', 'Participant', 'Total Points', 'Total Kill Points', 'Total Placement Points']].sort_values("Rank"),
    use_container_width=True,
    hide_index=True
)
st.divider()
st.subheader("Points Progression Across Games")

games_df = pd.read_csv("data/games_long_clean.csv")

all_teams = games_df["Participant"].unique().tolist()
selected_teams = st.multiselect(
    "Select teams to compare",
    options=all_teams,
    default=["4Thrives", "ULF Esports", "FURIA"]  # top 3 as a sensible default
)

filtered_games_df = games_df[games_df["Participant"].isin(selected_teams)]

fig3 = px.line(
    filtered_games_df,
    x="Game",
    y="Cumulative Points",
    color="Participant",
    title="Cumulative Points by Game (Grand Finals)",
    markers=True
)
fig3.update_layout(xaxis=dict(dtick=1))
st.plotly_chart(fig3, use_container_width=True)
st.divider()
st.header("Player Stats — Grand Finals")

players_df = pd.read_csv("data/player_stats_clean.csv")

# --- Team filter ---
all_teams_p = ["All Teams"] + sorted(players_df["Team"].unique().tolist())
selected_team = st.selectbox("Filter by team", all_teams_p)

if selected_team != "All Teams":
    filtered_players_df = players_df[players_df["Team"] == selected_team]
else:
    filtered_players_df = players_df

# --- Stat cards ---
pcol1, pcol2, pcol3 = st.columns(3)
top_fragger = filtered_players_df.loc[filtered_players_df["Elims"].idxmax()]
best_kd = filtered_players_df.loc[filtered_players_df["KD Ratio"].idxmax()]
pcol1.metric("Players Shown", len(filtered_players_df))
pcol2.metric("Top Fragger", f"{top_fragger['Player']} ({top_fragger['Elims']})")
pcol3.metric("Best KD Ratio", f"{best_kd['Player']} ({best_kd['KD Ratio']})")

# --- Top 10 Elims chart ---
top10_elims = filtered_players_df.sort_values("Elims", ascending=False).head(10)
fig4 = px.bar(
    top10_elims.sort_values("Elims", ascending=True),
    x="Elims",
    y="Player",
    orientation="h",
    title="Top 10 Fraggers (Eliminations)",
    hover_data=["Team", "KD Ratio"]
)
st.plotly_chart(fig4, use_container_width=True)

# --- Full player table ---
st.subheader("All Players")
st.dataframe(
    filtered_players_df.sort_values("Elims", ascending=False),
    use_container_width=True
)