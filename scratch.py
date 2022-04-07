# Grouped bar - Programs
col1, col2 = st.columns(2)
grp_prg = df_sub_pl.groupby(["Program Name"]).agg({"Employee Number": "nunique", "%": "sum"}).reset_index().rename(columns={"Employee Number": "Head Count", "%": "FTE Contribution"}).sort_values("Program Name", ascending=False).reset_index(drop=True)
grp_prg["color"] = grp_prg["Program Name"].map(prg_color_map)
grp_prg = grp_prg[(grp_prg["Head Count"] > 0) & (grp_prg["FTE Contribution"] > 0)]

if len(df_sub_pl["Program Name"].unique()) >= 15:
    height = 550
else:
    height = 400
fig = px.bar(grp_prg, x=["Head Count", "FTE Contribution"], y="Program Name", orientation="h", barmode="group", color_discrete_sequence=alt2palette, height=height)
fig.update_layout(
    xaxis_title=None, yaxis_title=None,
    title=dict(
        text="FTE Contriubtion and Head Counts by Program",
        font=dict(size=title_size)),
    legend=dict(
        title=dict(text=None),
        traceorder="reversed",
        orientation="h",
        xanchor="center",
        yanchor="bottom",
        y=-0.25))
col1.plotly_chart(fig, use_container_width=True)

grp_team = df_sub_pl.groupby(["Team"]).agg({"Employee Number": "nunique", "%": "sum"}).reset_index().rename(columns={"Employee Number": "Head Count", "%": "FTE Contribution"}).sort_values("Team", ascending=False).reset_index(drop=True)
grp_team["color"] = grp_team["Team"].map(team_color_map)
grp_team = grp_team[(grp_team["Head Count"] > 0) & (grp_team["FTE Contribution"] > 0)]

if len(df_sub_pl["Team"].unique()) >= 15:
    height = 550
else:
    height = 400
fig = px.bar(grp_team, x=["Head Count", "FTE Contribution"], y="Team", orientation="h", barmode="group", color_discrete_sequence=alt2palette[2:], height=height)
fig.update_layout(
    xaxis_title=None, yaxis_title=None,
    title=dict(
        text="FTE Contriubtion and Head Counts by Team",
        font=dict(size=title_size)),
    legend=dict(
        title=dict(text=None),
        traceorder="reversed",
        orientation="h",
        xanchor="center",
        yanchor="bottom",
        y=-0.25))
col2.plotly_chart(fig, use_container_width=True)



# Stacked bar - Manual Level
col1, col2 = st.columns(2)
chart_height = 600
grp_prg_ml = df_sub_pl.groupby(["Senior Leader", "Manual Level"]).agg({"Employee Number": "nunique", "%": "sum"}).reset_index().rename(columns={"Employee Number": "Head Count", "%": "FTE Contribution"}).sort_values(["Senior Leader", "Manual Level"], ascending=[False, True]).reset_index(drop=True)
grp_prg_ml["color"] = grp_prg_ml["Manual Level"].map(ml_color_map)
grp_prg_ml = grp_prg_ml[(grp_prg_ml["Head Count"] > 0) & (grp_prg_ml["FTE Contribution"] > 0)]

fig = f.chart_h_stacked_bars(agged_data=grp_prg_ml, df_values=df_values, stacked_col="Manual Level", xcol="FTE Contribution", ycol="Senior Leader", orientation="h", color_map=ml_color_map, height=chart_height, title="FTEs by Manual Level/Senior Manager", title_size=title_size)
col1.plotly_chart(fig, use_container_width=True)

fig = f.chart_h_stacked_bars(agged_data=grp_prg_ml, df_values=df_values, stacked_col="Manual Level", xcol="Head Count", ycol="Senior Leader", orientation="h", color_map=ml_color_map, height=chart_height, title="Head Count by Manual Level/Senior Manager", title_size=title_size)
col2.plotly_chart(fig, use_container_width=True)




Map
prd_line_geo = f.agg_data_count_fte(df, ["Quarter", "Country", "Product Line"], ["Head Count"], color_pl_map, ascending=False)

fig = f.chart_map(prd_line_geo, color="Product Line", color_map=color_pl_map, size="Head Count", title="Product Line Head Count by Location", title_size=title_size)

col1.plotly_chart(fig, use_container_width=True)

prd_line_srLeader = df.groupby(["Quarter", "Product Line", "Senior Leader"]).agg({"Program Name": "nunique", "Employee Number": "nunique", "%": "sum"}).reset_index().sort_values("Senior Leader")

# fig = go.Figure()
# for i in range(len(df_values["Senior Leader"])):
#     nm = df_values["Senior Leader"][i]
#     df_sub = prd_line_srLeader[prd_line_srLeader["Senior Leader"] == nm]
#     fig.add_trace(go.Bar(
#         y=df_sub["Product Line"],
#         x=df_sub["%"],
#         name=nm,
#         text=df_sub["Senior Leader"],
#         hovertemplate="%{text}=%{x} FTEs<extra></extra>",
#         textposition="none",
#         # marker=dict(color=base_palette[i]),
#         orientation="h"
#     ))




# Product Line by FTE Contribution Pie Chart
prg_pl = df.groupby(["Quarter", "Product Line"]).agg({"Program Name": "count", "Employee Number": "nunique", "%": "sum"}).reset_index().rename(columns={"Employee Number": "Head Count", "%": "FTE Contribution", "Program Name": "Program Count"})
prg_pl["color"] = prg_pl["Product Line"].map(color_pl_map)
fig = go.Figure(
    data=[go.Pie(
        labels=prg_pl["Product Line"],
        values=prg_pl["Program Count"],
        hole=0.4,
        text=prg_pl["Product Line"],
        textfont=dict(
            size=11),
        hovertemplate="%{label}<br>" + "FTE Count=%{value}<br>" + "Pct=%{percent}",
        marker=dict(
            base_palette=prg_pl["color"]))])
fig.update_layout(
    height=550,
    uniformtext_minsize=8,
    uniformtext_mode="hide",
    showlegend=False,
    title=dict(
        text="Programs in Product Line",
        yanchor="top",
        y=.98,
        xanchor="left",
        font=dict(
            size=title_size))
)
col2.plotly_chart(fig, use_container_width=True)

col1, col2 = st.columns(2)
col1.markdown("""
    ##### Question: How are Product Line team members geographically distributed?

    Can we work more efficiently by distributing product line work in similar timezones?""")
col2.markdown("""
    ##### Question: How many programs are in each Product Line?

    What Product Lines have the most moving parts?""")
st.markdown("---")

col1, col2 = st.columns(2)
# Level Bar Chart
role_pl = agg_data_count_fte(df, ["Quarter", "Manual Level", "Product Line"], ["FTE Contribution"], color_pl_map, ascending=False)
fig = go.Figure()
for i in range(len(df_values["Manual Level"])):
    pl = df_values["Manual Level"][i]
    df_sub = role_pl[role_pl["Manual Level"] == pl]
    fig.add_trace(go.Bar(
        y=df_sub["Product Line"],
        x=df_sub["FTE Contribution"],
        name=pl,
        text=df_sub["Manual Level"],
        hovertemplate="%{text}=%{x} FTEs<extra></extra>",
        insidetextfont=dict(size=1),
        textposition="none",
        marker=dict(color=base_palette[i]),
        orientation="h"
    ))
fig.update_layout(
    barmode="stack",
    height=600,
    yaxis=dict(
        categoryorder="category descending",
        title="Role Level"),
    title=dict(
        text="Role Level FTEs by Product Line",
        font=dict(
            size=title_size))
)
col1.plotly_chart(fig, use_container_width=True)

# Head Count/FTE Contribution by Program Count Scatter Plot
pl_fte = df.groupby(["Quarter", "Product Line"]).agg({"Program Name": "nunique", "Employee Number": "nunique", "%": "sum"}).reset_index().rename(columns={"Program Name": "Program Count", "Employee Number": "Head Count", "%": "FTE Contribution"})
pl_fte = pl_fte.sort_values("Product Line").reset_index(drop=True)
pl_fte["color"] = pl_fte["Product Line"].map(color_pl_map)

fig = go.Figure()
for i in range(len(df_values["Product Line"])):
    pl = df_values["Product Line"][i]
    df_sub = pl_fte[pl_fte["Product Line"] == pl]
    fig.add_trace(go.Scatter(
        x=df_sub["Head Count"],
        y=df_sub["FTE Contribution"],
        name=pl,
        text=df_sub["Product Line"],
        hovertemplate="%{text}<br>" + "Head Count=%{x}<br>" + "FTE Contribution=%{y}<br>" + "Program Count=%{marker.size:,}" + "<extra></extra>",
        mode="markers",
        marker=dict(
            size=df_sub["Program Count"],
            sizemin=5,
            sizeref=.2,
            color=base_palette[i])))
fig.update_layout(
    height=600,
    xaxis=dict(
        title="Head Count"),
    yaxis=dict(
        title="FTE Contribution"),
    legend=(dict(
        itemsizing="constant")),
    title=dict(
        text="Product Line Head Count & FTEs by Program Count",
        font=dict(
            size=title_size))
)
col2.plotly_chart(fig, use_container_width=True)

col1, col2 = st.columns(2)
col1.markdown("""
    ##### Question: How are FTE units distributed in Product Lines by Role Level

    Are we top heavy in any product lines? Where do we need to reach a better ratio of IC to Manager to Executive?""")
col2.markdown("""
    ##### Question: Does Program Count impact Head Count and FTE Contribution?

    Bubbles are sized by Program Count in Product Line. We expect a higher Program Count to result in more Head Count (x axis) and more FTE Contribution (y axis). Smaller bubble that are closer to the top or right edges indicate relatively few projects for the Head Count/FTE Contribution. Similarly, larger bubbles near the left or bottom edges indicate relatively more projects for the Head Count/FTE Contribution.""")
st.markdown("---")

#
#
# Program Section
#
#

st.markdown("## Programs")
col1, col2 = st.columns(2)
select_prod_line = col1.multiselect("Product Lines", df_values["Product Line"], default=df_values["Product Line"][0])

filtered_programs = df[df["Product Line"].isin(select_prod_line)]["Program Name"].unique().tolist()
select_programs = col2.multiselect(
    "Programs",
    filtered_programs,
    default=filtered_programs,
    help="Choose Product Lines first to see filtered Programs")

prg_df = df[(df["Product Line"].isin(select_prod_line)) & (df["Program Name"].isin(select_programs))].sort_values("Employee Number").reset_index(drop=True)
prg_unique = unique_values_in_column(prg_df)
prg_unstacked = unstacked[unstacked["Employee Number"].isin(prg_unique["Employee Number"])].sort_values("Employee Number").reset_index(drop=True)
color_prg_map = color_map(prg_unique["Program Name"], base_palette)

col1, col2 = st.columns(2)

# Map Chart
geo_prg = prg_df.groupby(["Quarter", "Country", "Program Name"])[["Employee Number", "%"]].agg({"Employee Number": "nunique", "%": "sum"}).reset_index().rename(columns={"Employee Number": "Head Count", "%": "FTE Contribution"})
geo_prg = geo_prg.sort_values(["Head Count"], ascending=False).reset_index(drop=True)
geo_prg["color"] = geo_prg["Program Name"].map(color_prg_map)
fig = px.scatter_geo(geo_prg, locations="Country", color="Program Name", color_discrete_map=color_prg_map, size="Head Count", locationmode="country names", height=600, size_max=70, projection="natural earth", )
fig.update_layout(
    legend=dict(
        yanchor="bottom",
        y=-.05,
        xanchor="left",
        orientation="h"),
    title=dict(
        text="Country Head Count by Program Name",
        font=dict(
            size=title_size)))
col1.plotly_chart(fig, use_container_width=True)

# Teams in Programs Pie Chart
head_prg = prg_df.groupby(["Quarter", "Program Name"]).agg({"Team": "nunique", "Employee Number": "nunique", "%": "sum"}).reset_index().rename(columns={"Employee Number": "Head Count", "%": "FTE Contribution", "Team": "Number of Teams"})
head_prg["color"] = head_prg["Program Name"].map(color_prg_map)
fig = go.Figure(
    data=[go.Pie(
        labels=head_prg["Program Name"],
        values=head_prg["Head Count"],
        hole=0.4,
        # text=head_prg["Program Name"],
        textfont=dict(
            size=10),
        hovertemplate="%{label}<br>" + "Head Count=%{value}<br>" + "Pct=%{percent}" + "<extra></extra>",
        marker=dict(
            base_palette=head_prg["color"]))])
fig.update_layout(
    height=550,
    uniformtext_minsize=11,
    uniformtext_mode="hide",
    # showlegend=False,
    title=dict(
        text="Head Count by Program",
        yanchor="top",
        y=.98,
        xanchor="left",
        font=dict(
            size=title_size))
)
col2.plotly_chart(fig, use_container_width=True)
st.markdown("---")

col1, col2 = st.columns(2)
# Level Bar Chart
role_prg = prg_df.groupby(["Quarter", "Manual Level", "Program Name"])[["Employee Number", "%"]].agg({"Employee Number": "nunique", "%": "sum"}).reset_index().rename(columns={"Employee Number": "Head Count", "%": "FTE Contribution"})
role_prg = role_prg.sort_values("FTE Contribution").reset_index(drop=True)
role_prg["color"] = role_prg["Program Name"].map(color_prg_map)
levels = role_prg["Manual Level"].unique().tolist()
fig = go.Figure()
for i in range(len(levels)):
    prg = levels[i]
    df_sub = role_prg[role_prg["Manual Level"] == prg]
    fig.add_trace(go.Bar(
        y=df_sub["Program Name"],
        x=df_sub["FTE Contribution"],
        name=prg,
        text=df_sub["Manual Level"],
        hovertemplate="%{text}=%{x} FTEs<extra></extra>",
        insidetextfont=dict(size=1),
        textposition="none",
        marker=dict(color=base_palette[i]),
        orientation="h"
    ))
fig.update_layout(
    barmode="stack",
    height=600,
    yaxis=dict(
        categoryorder="category descending",
        title="Program Name"),
    title=dict(
        text="Role Level FTEs by Program Name",
        font=dict(
            size=title_size))
)
col1.plotly_chart(fig, use_container_width=True)

# Head Count/FTE Contribution by Number of Teams Scatter Plot
head_prg = head_prg.sort_values("Program Name").reset_index(drop=True)
head_prg["color"] = head_prg["Program Name"].map(color_prg_map)
levels = head_prg["Program Name"].unique().tolist()
fig = go.Figure()
for i in range(len(levels)):
    prg = levels[i]
    df_sub = head_prg[head_prg["Program Name"] == prg]
    fig.add_trace(go.Scatter(
        x=df_sub["Head Count"],
        y=df_sub["FTE Contribution"],
        name=prg,
        text=df_sub["Program Name"],
        hovertemplate="%{text}<br>" + "Head Count=%{x}<br>" + "FTE Contribution=%{y}<br>" + "Number of Teams=%{marker.size:,}" + "<extra></extra>",
        mode="markers",
        marker=dict(
            size=df_sub["Number of Teams"],
            sizemin=5,
            sizeref=.1,
            color=base_palette[i])))
fig.update_layout(
    height=600,
    xaxis=dict(
        title="Head Count"),
    yaxis=dict(
        title="FTE Contribution"),
    legend=dict(
        itemsizing="constant"),
    title=dict(
        text="Program Head Count & FTEs by Number of Teams",
        font=dict(
            size=title_size))
)
col2.plotly_chart(fig, use_container_width=True)

with st.expander("Expand for detailed table"):
    prg_unstacked
st.markdown("---")

#
#
# Teams Section
#
#
st.markdown("## Department: Teams")
col1, col2 = st.columns(2)
select_dept = col1.selectbox("Department", df_values["Dept"])
team_df = df[df["Dept"] == select_dept]

filtered_teams = team_df["Team"].unique().tolist()
select_team = col2.multiselect(
    "Team",
    filtered_teams,
    default=filtered_teams)
team_df = team_df[team_df["Team"].isin(select_team)].reset_index(drop=True)

team_unique = unique_values_in_column(team_df)
team_unstacked = unstacked[unstacked["Employee Number"].isin(team_unique["Employee Number"])].sort_values("Employee Number").reset_index(drop=True)

color_team_map = color_map(team_unique["Team"], base_palette)
color_level_map = color_map(team_unique["Manual Level"], base_palette)
st.header("")

# Cards
col1, col2, col3 = st.columns(3)
col1.metric("Heads", len(team_unstacked))
col2.metric("Programs", len(team_df["Program Name"].unique()))
col3.metric("Avg FTE Contribution", str(round(team_df[team_df["%"] > 0]["%"].mean() * 100, 2)) + "%")
st.header("")
col1, col2 = st.columns(2)
# Map
geo_teams = team_df.groupby(["Quarter", "Country", "Team"])[["Employee Number", "%"]].agg({"Employee Number": "nunique", "%": "sum"}).reset_index().rename(columns={"Employee Number": "Head Count", "%": "FTE Contribution"})
geo_teams = geo_teams.sort_values(["Head Count"], ascending=False).reset_index(drop=True)
geo_teams["color"] = geo_teams["Team"].map(color_team_map)

fig = chart_map(geo_teams, "Team", color_team_map, "Head Count", title_size, "Team Head Count by Location")
col1.plotly_chart(fig, use_container_width=True)

# Pie
color_tprg_map = color_map(team_unique["Program Name"], base_palette)
team_prg = team_df.groupby(["Quarter", "Program Name"]).agg({"Team": "nunique", "Employee Number": "nunique", "%": "sum"}).reset_index().rename(columns={"Employee Number": "Head Count", "%": "FTE Contribution", "Team": "Number of Teams"})
team_prg["color"] = team_prg["Program Name"].map(color_tprg_map)
fig = chart_pie(team_prg, "Program Name", "Head Count", title_size, "Head Count by Program", showlegend=True)
col2.plotly_chart(fig, use_container_width=True)
st.markdown("---")

col1, col2 = st.columns(2)
# Stacked bar
role_team = team_df.groupby(["Quarter", "Manual Level", "Team"]).agg({"Employee Number": "nunique", "%": "sum"}).reset_index().rename(columns={"Employee Number": "Head Count", "%": "FTE Contribution"})
role_team = role_team.sort_values("FTE Contribution").reset_index(drop=True)
role_team["color"] = role_team["Manual Level"].map(color_level_map)

fig = chart_h_stacked_bars(role_team, role_team["Manual Level"].unique().tolist(), "Manual Level", "Team", "FTE Contribution", "v", color_level_map, title_size, "Role Level FTEs by Team")
col1.plotly_chart(fig, use_container_width=True)

# Stacked bar
role_prg = team_df.groupby(["Quarter", "Program Name", "Manual Level"]).agg({"Employee Number": "nunique", "%": "sum"}).reset_index().rename(columns={"Employee Number": "Head Count", "%": "FTE Contribution"})
role_prg = role_prg.sort_values("Program Name").reset_index(drop=True)
role_prg["color"] = role_prg["Program Name"].map(color_tprg_map)
fig = chart_h_stacked_bars(role_prg, role_prg["Manual Level"].unique().tolist(), "Manual Level", "Program Name", "FTE Contribution", "v", color_level_map, title_size, "Role Level FTEs by Program")
col2.plotly_chart(fig, use_container_width=True)
with st.expander("Expand for detailed table"):
    team_unstacked[["Employee Name", "Business Card Title", "Manual Level", "Manager", "Senior Leader", "Team", "Dept", "Division", "Executive", "GeoZone", "Program Name 1", "Program 1 %", "Program Name 2", "Program 2 %"]]
team_df
team_unstacked
