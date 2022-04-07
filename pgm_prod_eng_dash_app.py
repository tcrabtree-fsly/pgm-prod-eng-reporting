import streamlit as st
import pandas as pd
from base_data import df, df_values, base_palette, darker_palette, alt2palette, unstacked
import funcs as f
from lorem import lorem
import plotly.express as px
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from pywaffle import Waffle
import random

# Settings
st.set_page_config(page_title="Product + Engineering Resource Status", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

# # Write to Sheet - Uncomment to write formatted data to sheet
# from base_data import write_formatted_data
# response = write_formatted_data(df, spreadsheet_id, "formatted_data")

# Palettes & Options
prd_line_color_map = f.color_map(df_values["Product Line"], base_palette)
srL_color_map = f.color_map(df_values["Senior Leader"], base_palette)
ml_color_map = f.color_map(df_values["Manual Level"], base_palette)
lvl_color_map = f.color_map(df_values["Level"], base_palette)
mlvl_color_map = f.color_map(df_values["Manual Level"], base_palette + darker_palette)
prg_color_map = f.color_map(df_values["Program Name"], base_palette)
team_color_map = f.color_map(df_values["Team"], base_palette)
title_size = 18

# Sidebar
st.sidebar.markdown("""
    # Contents
    * [Overview](#product-engineering-resource-status)
    * [Product Lines](#product-lines)
    * [Programs](#programs)
    * [Senior Leader](#senior-leader)

    # Chart Tips :bulb:""")
st.sidebar.info("""
    Most charts allow for zoom in/out :heavy_plus_sign: :heavy_minus_sign:, pan :left_right_arrow:, area select by box or lasso, and save as a png :camera:. Hover over a chart to see options in the upper left.

    :point_up: Single click legend item to toggle item display in chart

    :v: Double click legend item to toggle show only clicked item in chart

    Do you want to see a larger version :bar_chart:? The arrows in the far right corder when hovering will toggle a full screen view.""")

# Body
st.title("Product + Engineering Resource Status")

#
# Pgm-ProdOps-ENG Overview
#
st.markdown("## Overview")
col1, col2, col3 = st.columns(3)
total_counts = df.groupby("Quarter").agg("nunique")
fig = go.Figure(go.Indicator(value=total_counts["Product Line"].values[0], mode="number", title="Product Lines"))
fig.update_layout(height=250)
col1.plotly_chart(fig, use_container_width=True)
fig = go.Figure(go.Indicator(value=total_counts["Program Name"].values[0], mode="number", title="Programs"))
fig.update_layout(height=250)
col2.plotly_chart(fig, use_container_width=True)
fig = go.Figure(go.Indicator(value=total_counts["Employee Number"].values[0], mode="number", title="Head Count"))
fig.update_layout(height=250)
col3.plotly_chart(fig, use_container_width=True)

# Waffle - Head Count by Manual Level
st.markdown("### Head Count by Manual Level")
mlevel_sort = df.groupby(["Level", "Manual Level"]).size().rename("Count").reset_index()
mlevel_sort["group"] = mlevel_sort["Level"].apply(lambda x: x[0])
mlevel_sort = mlevel_sort.sort_values(["group", "Level", "Manual Level"], ascending=[True, False, True])
mlevel_grp_dict = pd.DataFrame(mlevel_sort["Manual Level"].unique()).rename(columns={0: "mlevel"}).reset_index()
mlevel_grp_dict = dict(zip(mlevel_grp_dict["mlevel"], mlevel_grp_dict["index"]))
mlevel_sort = mlevel_sort.groupby(["Manual Level"])["Count"].sum().rename("Count").reset_index().reset_index(drop=True)
mlevel_sort["order"] = mlevel_sort["Manual Level"].map(mlevel_grp_dict)
mlevel_sort["color"] = mlevel_sort["Manual Level"].map(mlvl_color_map)
mlevel_sort = mlevel_sort.sort_values("order").reset_index(drop=True)
mlevel_sum = mlevel_sort["Count"].sum()
labels = list(zip(mlevel_sort["Manual Level"], mlevel_sort["Count"]))
labels = [f"{i[0]}: {i[1]} ({round(i[1] / mlevel_sum * 100, 2)}%)" for i in labels]

fig = plt.figure(
    FigureClass=Waffle,
    rows=9,
    values=mlevel_sort["Count"].tolist(),
    colors=mlevel_sort["color"].tolist(),
    icons="user",
    font_size=8,
    icon_legend=True,
    starting_location="NW",
    legend=dict(
        labels=labels,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.15),
        ncol=4,
        fontsize=4,
        framealpha=0
    )
)
st.pyplot(fig, use_container_width=True)
st.markdown("---")

#
# Product Line Section
#
st.markdown("""## Product Lines""")
# Group Bar - Head/FTE
st.markdown("### Total Head Count & FTE Contribution by Product Line")
grp_pl = df.groupby(["Product Line"]).agg({"Employee Number": "nunique", "%": "sum"}).reset_index().rename(columns={"Employee Number": "Head Count", "%": "FTE Contribution"}).sort_values(["Product Line"], ascending=True).reset_index(drop=True)
fig = px.bar(grp_pl, x=["Head Count", "FTE Contribution"], y="Product Line", orientation="h", barmode="group", color_discrete_sequence=alt2palette, height=450)
fig.update_layout(
    xaxis_title=None, yaxis_title=None,
    yaxis=dict(categoryorder="category descending"),
    title=dict(
        # text="FTE Contriubtion and Head Counts by Product Line",
        text=None,
        font=dict(size=title_size)),
    legend=dict(
        title=dict(text=None),
        traceorder="reversed",
        # orientation="h",
        # xanchor="center",
        # yanchor="bottom",
        # y=-0.25
    ))
st.plotly_chart(fig, use_container_width=True)

# Product Drill
select_pl = st.selectbox("Product Line", df_values["Product Line"])
df_sub_pl = df[df["Product Line"].isin([select_pl])]
st.markdown(f"""### {select_pl} Overview""")
col1, col2, col3, col4 = st.columns((1, 1, 1, 3.5))
col4.markdown(f"{lorem[random.randrange(9)]}")
col1.metric("Program Count", len(df_sub_pl["Program Name"].unique()))
col2.metric("Head Count", len(df_sub_pl["Employee Number"].unique()))
col3.metric("FTEs", df_sub_pl["%"].sum())

#  Stacked bar - Manual Level
st.markdown("#### FTE & Head Count")
grp_pl_mlevel = df_sub_pl.groupby(["Manual Level"]).agg({"Employee Number": "nunique", "%": "sum"}).reset_index().rename(columns={"Employee Number": "Head Count", "%": "FTE Contribution"}).sort_values(["Manual Level"], ascending=False).reset_index(drop=True)
grp_pl_mlevel["y1"] = "Head Count"
grp_pl_mlevel["y2"] = "FTE Contribution"
fig = go.Figure()
for i in range(len(df_values["Manual Level"])):
    nm = df_values["Manual Level"][i]
    df_ = grp_pl_mlevel[grp_pl_mlevel["Manual Level"] == nm]
    fig.add_trace(go.Bar(
        y=df_["y2"],
        x=df_["FTE Contribution"],
        name=nm,
        text=df_["Manual Level"],
        textposition="none",
        hovertemplate="%{text}=%{x} FTEs<extra></extra>",
        marker=dict(color=ml_color_map[nm]),
        orientation="h"
    ))
for i in range(len(df_values["Manual Level"])):
    nm = df_values["Manual Level"][i]
    df_ = grp_pl_mlevel[grp_pl_mlevel["Manual Level"] == nm]
    fig.add_trace(go.Bar(
        y=df_["y1"],
        x=df_["Head Count"],
        name=nm,
        text=df_["Manual Level"],
        textposition="none",
        hovertemplate="%{text}=%{x} head count<extra></extra>",
        marker=dict(color=ml_color_map[nm]),
        orientation="h",
        showlegend=False
    ))
fig.update_layout(
    barmode="stack",
    height=450,
    yaxis=dict(categoryorder="category descending"),
    title=dict(
        text="Distribution by Manual Level",
        font=dict(size=title_size)),
    legend=dict(traceorder="normal")
)
st.plotly_chart(fig, use_container_width=True)
st.markdown(f"{lorem[random.randrange(9)]}")

# Program FTE Count by Product Line
grp_pl_prg = df_sub_pl.groupby(["Quarter", "Program Name"]).agg({"Employee Number": "nunique", "%": "sum"}).reset_index().rename(columns={"Employee Number": "Head Count", "%": "FTE Contribution"}).sort_values(["FTE Contribution"], ascending=False).reset_index(drop=True)
grp_pl_prg["color"] = grp_pl_prg["Program Name"].map(prg_color_map)

col1, col2 = st.columns(2)
fig = px.bar(grp_pl_prg, x="Program Name", y="FTE Contribution", orientation="v", color="Program Name", color_discrete_map=prg_color_map)
fig.update_layout(
    height=500,
    title=dict(
        text="Program FTEs",
        font=dict(size=title_size)),
    legend=dict(
        title=dict(text=None))
)
fig.update_yaxes(title=dict(text=None))
col1.plotly_chart(fig, use_container_width=True)

# Program Count by Sr Leader
grp_pl_prg_ml = df_sub_pl.groupby(["Quarter", "Product Line", "Senior Leader"])["Program Name"].nunique().reset_index().rename(columns={"Program Name": "Program Count"}).sort_values(["Product Line", "Senior Leader"], ascending=True).reset_index(drop=True)
grp_pl_prg_ml["color"] = grp_pl_prg_ml["Senior Leader"].map(srL_color_map)

fig = px.bar(grp_pl_prg_ml, x="Program Count", y="Senior Leader", orientation="h", color="Senior Leader", color_discrete_map=srL_color_map)
fig.update_layout(
    height=500,
    title=dict(
        text="Program Count by Senior Leader", 
        font=dict(size=title_size)),
    legend=dict(
        title=dict(text=None))
)
fig.update_yaxes(title=dict(text=None))
col2.plotly_chart(fig, use_container_width=True)

with st.expander("Product Line table"):
    st.dataframe(unstacked[unstacked["Employee Number"].isin(df_sub_pl["Employee Number"].unique())][["Employee Name", "Manual Level", "Team", "Manager", "Senior Leader", "Quarter", "Program Name 1", "Program Name 2", "Program 1 %", "Program 2 %"]].sort_values(["Senior Leader", "Team", "Employee Name"]).reset_index(drop=True), height=500)
st.markdown("""---""")

#
# Programs Section
#
st.markdown("""## Programs""")

# Group Bar - Head/FTE
st.markdown("### Program FTEs")
grp_prg = df.copy()
grp_prg["Program Name"] = grp_prg["Product Line"] + ": " + grp_prg["Program Name"]
grp_prg = grp_prg.groupby(["Program Name"]).agg({"Employee Number": "nunique", "%": "sum"}).reset_index().rename(columns={"Employee Number": "Head Count", "%": "FTE Contribution"}).sort_values(["Program Name"], ascending=True).reset_index(drop=True)

prg_color_map_alt = {}
for c in grp_prg["Program Name"].unique():
    pl = c.split(": ")[0]
    v = prd_line_color_map[pl]
    prg_color_map_alt[c] = v

fig = px.bar(grp_prg, y="FTE Contribution", x="Program Name", orientation="v", barmode="stack", color="Program Name", color_discrete_map=prg_color_map_alt, height=650)
fig.update_layout(
    xaxis_title=None, yaxis_title=None,
    xaxis=dict(tickfont=dict(size=10), tickangle=65),
    title=dict(
        text=None,
        font=dict(size=title_size)),
    showlegend=False
)
st.plotly_chart(fig, use_container_width=True)

zip_sort = df.groupby(["Product Line", "Program Name"]).size().reset_index()
zip_sort = zip_sort[["Product Line", "Program Name"]].to_dict()
sort_by_pl = list(zip(zip_sort["Product Line"].values(), zip_sort["Program Name"].values()))
sort_by_pl = [f"{i[0]}: {i[1]}" for i in sort_by_pl]

select_prg = st.selectbox("Program", sort_by_pl)
df_sub_prg = df[df["Program Name"] == select_prg.split(":")[1].strip()]

st.markdown(f"""### {select_prg} Program Overview""")
col1, col2, col3 = st.columns((1, 1, 3.5))
col1.metric("Head Count", len(df_sub_prg["Employee Number"].unique()))
col2.metric("FTEs", df_sub_prg["%"].sum())
col3.markdown(f"{lorem[random.randrange(9)]}")

col1, col2 = st.columns((1, 3))
col1.markdown(f"""
    ### Location Distribution by Team
    {lorem[random.randrange(9)]}""")

grp_prg_geo = df_sub_prg.groupby(["Quarter", "Country", "Team"]).agg({"Employee Number": "nunique", "%": "sum"}).reset_index().rename(columns={"Employee Number": "Head Count", "%": "FTE Contribution"}).sort_values(["Head Count"], ascending=False).reset_index(drop=True)
fitbounds = None
if len(grp_prg_geo["Country"].unique()) > 1:
    fitbounds = "locations"

fig = f.chart_map(agged_data=grp_prg_geo, color="Team", color_map=team_color_map, size="Head Count", size_max=45, title="Teams by Location", title_size=title_size)
fig.update_layout(
    title=dict(text=None),
    legend=dict(title=dict(text=None), yanchor="top", y=.9),
    height=400,
    geo=dict(fitbounds=fitbounds)
)
col2.plotly_chart(fig, use_container_width=True)

#  Stacked bar - Manual Level
st.markdown("#### FTE & Head Count")
grp_prg_mlevel = df_sub_prg.groupby(["Manual Level"]).agg({"Employee Number": "nunique", "%": "sum"}).reset_index().rename(columns={"Employee Number": "Head Count", "%": "FTE Contribution"}).sort_values(["Manual Level"], ascending=False).reset_index(drop=True)
grp_prg_mlevel["y1"] = "Head Count"
grp_prg_mlevel["y2"] = "FTE Contribution"
fig = go.Figure()
for i in range(len(df_values["Manual Level"])):
    nm = df_values["Manual Level"][i]
    df_ = grp_prg_mlevel[grp_prg_mlevel["Manual Level"] == nm]
    fig.add_trace(go.Bar(
        y=df_["y2"],
        x=df_["FTE Contribution"],
        name=nm,
        text=df_["Manual Level"],
        textposition="none",
        hovertemplate="%{text}=%{x} FTEs<extra></extra>",
        marker=dict(color=ml_color_map[nm]),
        orientation="h"
    ))
# for i in range(len(df_values["Manual Level"])):
#     nm = df_values["Manual Level"][i]
#     df_ = grp_prg_mlevel[grp_prg_mlevel["Manual Level"] == nm]
#     fig.add_trace(go.Bar(
#         y=df_["y1"],
#         x=df_["Head Count"],
#         name=nm,
#         text=df_["Manual Level"],
#         textposition="none",
#         hovertemplate="%{text}=%{x} head count<extra></extra>",
#         marker=dict(color=ml_color_map[nm]),
#         orientation="h",
#         showlegend=False
#     ))
fig.update_layout(
    barmode="stack",
    height=450,
    yaxis=dict(categoryorder="category descending"),
    title=dict(
        text="Distribution by Manual Level",
        font=dict(size=title_size)),
    legend=dict(traceorder="normal")
)
st.plotly_chart(fig, use_container_width=True)

# Grouped bar - Sr Leader
col1, col2 = st.columns(2)
grp_prg_srl = df_sub_prg.groupby(["Senior Leader"]).agg({"Employee Number": "nunique", "%": "sum"}).reset_index().rename(columns={"Employee Number": "Head Count", "%": "FTE Contribution"}).sort_values("Senior Leader", ascending=False).reset_index(drop=True)
grp_prg_srl["color"] = grp_prg_srl["Senior Leader"].map(srL_color_map)
grp_prg_srl = grp_prg_srl[(grp_prg_srl["Head Count"] > 0) & (grp_prg_srl["FTE Contribution"] > 0)]

fig = px.bar(grp_prg_srl, y="FTE Contribution", x="Senior Leader", orientation="v", barmode="stack", color="Senior Leader", color_discrete_map=srL_color_map, height=500)
fig.update_layout(
    xaxis_title=None, yaxis_title=None,
    yaxis=(dict(categoryorder="category descending")),
    showlegend=False,
    title=dict(
        text="FTEs by Senior Leader",
        font=dict(size=title_size)),
)
col1.plotly_chart(fig, use_container_width=True)

# Grouped bar - Team
grp_prg_team = df_sub_prg.groupby(["Team"]).agg({"Employee Number": "nunique", "%": "sum"}).reset_index().rename(columns={"Employee Number": "Head Count", "%": "FTE Contribution"}).sort_values("Team", ascending=False).reset_index(drop=True)
grp_prg_team["color"] = grp_prg_team["Team"].map(team_color_map)
grp_prg_team = grp_prg_team[(grp_prg_team["Head Count"] > 0) & (grp_prg_team["FTE Contribution"] > 0)]

fig = px.bar(grp_prg_team, x="FTE Contribution", y="Team", orientation="h", barmode="stack", color="Team", color_discrete_map=team_color_map, height=500)
fig.update_layout(
    xaxis_title=None, yaxis_title=None,
    yaxis=(dict(categoryorder="category descending")),
    showlegend=False,
    title=dict(
        text="FTEs by Team",
        font=dict(size=title_size)),
)
col2.plotly_chart(fig, use_container_width=True)

with st.expander("Programs table"):
    # select_sl_tbl = st.selectbox("Filter by Senior Leader", df_sub_prg["Senior Leader"].unique())
    # df_tbl = df_sub_prg[df_sub_prg["Senior Leader"] == select_sl_tbl]
    st.dataframe(unstacked[unstacked["Employee Number"].isin(df_sub_prg["Employee Number"].unique())][["Employee Name", "Manual Level", "Team", "Manager", "Senior Leader", "Quarter", "Program Name 1", "Program Name 2", "Program 1 %", "Program 2 %"]].sort_values(["Senior Leader", "Team", "Employee Name"]).reset_index(drop=True), height=500)
st.markdown("---")

#
# Sr Leader Section
#
st.markdown("## Senior Leader")
# Group Bar - Head/FTE
st.markdown("### Head Count by Senior Leader")
grp_srl = df.groupby(["Senior Leader"]).agg({"Employee Number": "nunique", "%": "sum"}).reset_index().rename(columns={"Employee Number": "Head Count", "%": "FTE Contribution"}).sort_values(["Senior Leader"], ascending=True).reset_index(drop=True)
fig = px.bar(grp_srl, y="Head Count", x="Senior Leader", color="Senior Leader", orientation="v", barmode="group", color_discrete_map=srL_color_map, height=450)
fig.update_layout(
    xaxis_title=None, yaxis_title=None,
    yaxis=dict(categoryorder="category descending"),
    title=dict(
        text=None,
        font=dict(size=title_size)),
    legend=dict(
        title=dict(text=None),
    ))
fig.update_traces(width=1)
st.plotly_chart(fig, use_container_width=True)

select_srl = st.selectbox("Senior Leader", df["Senior Leader"].unique())
df_sub_srl = df[df["Senior Leader"] == select_srl]

name = select_srl
if len(select_srl.split(", ")) > 1:
    name = f"{select_srl.split(', ')[1]} {select_srl.split(', ')[0]}"

st.markdown(f"""### {name} Overview""")
col1, col2, col3, col4 = st.columns((1, 1, 1, 2.5))
col1.metric("Product Line Count", len(df_sub_srl["Product Line"].unique()))
col2.metric("Program Count", len(df_sub_srl["Program Name"].unique()))
col3.metric("Head Count", len(df_sub_srl["Employee Number"].unique()))
col4.markdown(f"{lorem[random.randrange(9)]}")

# Waffle - Head Count by Manual Level
st.markdown("#### Head Count Overview")
mlevel_sort = df_sub_srl.groupby(["Level", "Manual Level"]).size().rename("Count").reset_index()
mlevel_sort["group"] = mlevel_sort["Level"].apply(lambda x: x[0])
mlevel_sort = mlevel_sort.sort_values(["group", "Level", "Manual Level"], ascending=[True, False, True])
mlevel_grp_dict = pd.DataFrame(mlevel_sort["Manual Level"].unique()).rename(columns={0: "mlevel"}).reset_index()
mlevel_grp_dict = dict(zip(mlevel_grp_dict["mlevel"], mlevel_grp_dict["index"]))
mlevel_sort = mlevel_sort.groupby(["Manual Level"])["Count"].sum().rename("Count").reset_index().reset_index(drop=True)
mlevel_sort["order"] = mlevel_sort["Manual Level"].map(mlevel_grp_dict)
mlevel_sort["color"] = mlevel_sort["Manual Level"].map(mlvl_color_map)
mlevel_sort = mlevel_sort.sort_values("order").reset_index(drop=True)
mlevel_sum = mlevel_sort["Count"].sum()

labels = list(zip(mlevel_sort["Manual Level"], mlevel_sort["Count"]))
labels = [f"{i[0]}: {i[1]} ({round(i[1] / mlevel_sum * 100, 2)}%)" for i in labels]
fig = plt.figure(
    FigureClass=Waffle,
    columns=20,
    values=mlevel_sort["Count"].tolist(),
    colors=mlevel_sort["color"].tolist(),
    icons="user",
    font_size=12,
    icon_legend=True,
    starting_location="NW",
    legend=dict(
        labels=labels,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.15),
        ncol=3,
        fontsize=4,
        framealpha=0
    )
)
st.pyplot(fig, use_container_width=True)

st.markdown("""#### Head Count by Product Line & Program""")
# Stacked bar - Manual Level
col1, col2 = st.columns(2)
chart_height = 450
grp_srl_pl_mlevel = df_sub_srl.groupby(["Product Line", "Manual Level"]).agg({"Employee Number": "nunique", "%": "sum"}).reset_index().rename(columns={"Employee Number": "Head Count", "%": "FTE Contribution"}).sort_values(["Product Line", "Manual Level"], ascending=True)
grp_srl_pl_mlevel["color"] = grp_srl_pl_mlevel["Manual Level"].map(ml_color_map)
grp_srl_pl_mlevel = grp_srl_pl_mlevel[(grp_srl_pl_mlevel["Head Count"] > 0) & (grp_srl_pl_mlevel["FTE Contribution"] > 0)]
fig = f.chart_h_stacked_bars(agged_data=grp_srl_pl_mlevel, df_values=df_values, stacked_col="Manual Level", xcol="Head Count", ycol="Product Line", orientation="h", color_map=ml_color_map, height=chart_height, title="Head Count by Product Line", title_size=title_size)
fig.update_layout(legend=dict(traceorder="normal"))
col1.plotly_chart(fig, use_container_width=True)

grp_srl_prg_mlevel = df_sub_srl.groupby(["Program Name", "Manual Level"]).agg({"Employee Number": "nunique", "%": "sum"}).reset_index().rename(columns={"Employee Number": "Head Count", "%": "FTE Contribution"}).sort_values(["Program Name", "Manual Level"], ascending=True)
grp_srl_prg_mlevel["color"] = grp_srl_prg_mlevel["Manual Level"].map(ml_color_map)
grp_srl_prg_mlevel = grp_srl_prg_mlevel[(grp_srl_prg_mlevel["Head Count"] > 0) & (grp_srl_prg_mlevel["FTE Contribution"] > 0)]
fig = f.chart_h_stacked_bars(agged_data=grp_srl_prg_mlevel, df_values=df_values, stacked_col="Manual Level", xcol="Head Count", ycol="Program Name", orientation="h", color_map=ml_color_map, height=chart_height, title="Head Count by Program", title_size=title_size)
fig.update_layout(legend=dict(traceorder="normal"))
col2.plotly_chart(fig, use_container_width=True)

with st.expander("Senior Leader table"):
    st.dataframe(unstacked[unstacked["Employee Number"].isin(df_sub_srl["Employee Number"].unique())][["Employee Name", "Manual Level", "Team", "Manager", "Senior Leader", "Quarter", "Program Name 1", "Program Name 2", "Program 1 %", "Program 2 %"]].sort_values(["Manager", "Team", "Employee Name"]).reset_index(drop=True), height=500)
st.markdown("""---""")


