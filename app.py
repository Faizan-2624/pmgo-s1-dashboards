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
st.divider()
st.header("Map Performance — Grand Finals")

maps_df = pd.read_csv("data/map_performance_clean.csv")

selected_map = st.selectbox("Select a map", maps_df["Map"].unique())
map_filtered = maps_df[maps_df["Map"] == selected_map].sort_values("Total Points", ascending=False)

# --- Best team on this map ---
best_team = map_filtered.iloc[0]
st.metric(f"Top team on {selected_map}", best_team["Participant"], f"{best_team['Total Points']} pts")

# --- Bar chart: Total Points by team, for selected map ---
fig5 = px.bar(
    map_filtered.sort_values("Total Points", ascending=True),
    x="Total Points",
    y="Participant",
    orientation="h",
    title=f"Team Points on {selected_map}",
    hover_data=["Avg Placement", "Avg Elims", "Matches Played"]
)
st.plotly_chart(fig5, use_container_width=True)

# --- Compare average placement vs average elims across maps ---
st.subheader("Average Elims by Map (Top 10 Teams)")
top10_teams = maps_df.groupby("Participant")["Total Points"].sum().nlargest(10).index
compare_df = maps_df[maps_df["Participant"].isin(top10_teams)]

fig6 = px.bar(
    compare_df,
    x="Participant",
    y="Avg Elims",
    color="Map",
    barmode="group",
    title="Average Elims per Map — Top 10 Teams"
)
st.plotly_chart(fig6, use_container_width=True)
st.divider()
st.header("Advanced Stats — Grand Finals")

team_adv_df = pd.read_csv("data/team_advanced_stats_clean.csv")
player_adv_df = pd.read_csv("data/player_advanced_stats_clean.csv")

tab1, tab2 = st.tabs(["Team Advanced Stats", "Player Advanced Stats"])

with tab1:
    metric_choice = st.selectbox(
        "Compare teams by:",
        ["Damage Dealt", "Damage Received", "Healing Done", "Headshots", "Knocks", "Distance Traveled"]
    )
    fig7 = px.bar(
        team_adv_df.sort_values(metric_choice, ascending=True),
        x=metric_choice,
        y="Team",
        orientation="h",
        title=f"Team {metric_choice}"
    )
    st.plotly_chart(fig7, use_container_width=True)

    st.dataframe(team_adv_df.sort_values("Rank"), use_container_width=True)

with tab2:
    selected_player = st.selectbox("Select a player", sorted(player_adv_df["Player"].unique()))
    
    player_row = player_adv_df[player_adv_df["Player"] == selected_player].iloc[0]
    
    st.subheader(f"{selected_player} — {player_row['Team']}")
    
    pcol1, pcol2, pcol3, pcol4 = st.columns(4)
    pcol1.metric("Elims", int(player_row["Elims"]))
    pcol2.metric("KD Ratio", player_row["KD Ratio"])
    pcol3.metric("Avg Dmg Dealt", int(player_row["Avg Dmg Dealt"]))
    pcol4.metric("Headshots", int(player_row["Headshots"]))
    
    # Pick the stats worth comparing visually (skip IDs and things that don't make sense on one scale)
    stat_cols = [
        "Elims", "Assists", "Knocks", "Headshots", "Deaths",
        "Smokes Used", "Grenades Used", "Grenade Elims",
        "Teammates Rescued" if "Teammates Rescued" in player_adv_df.columns else None,
        "Airdrops Taken"
    ]
    stat_cols = [c for c in stat_cols if c is not None]
    
    stats_chart_df = pd.DataFrame({
        "Stat": stat_cols,
        "Value": [player_row[c] for c in stat_cols]
    })
    
    fig8 = px.bar(
        stats_chart_df,
        x="Stat",
        y="Value",
        title=f"{selected_player}'s Match Stats"
    )
    st.plotly_chart(fig8, use_container_width=True)
    
    # Distance stats separately since they're on a totally different scale (meters vs counts)
    st.subheader("Distance Covered")
    dist_df = pd.DataFrame({
        "Type": ["Driven", "Walked", "Traveled"],
        "Distance": [player_row["Distance Driven"], player_row["Distance Walked"], player_row["Distance Traveled"]]
    })
    fig9 = px.bar(dist_df, x="Type", y="Distance", title=f"{selected_player}'s Distance (meters)")
    st.plotly_chart(fig9, use_container_width=True)
    
    st.dataframe(player_adv_df.sort_values("Elims", ascending=False), use_container_width=True)