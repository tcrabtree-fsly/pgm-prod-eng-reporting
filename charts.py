import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pywaffle import Waffle
import matplotlib.pyplot as plt


# Functions
def chart_map(agged_data, color, color_map, size, size_max, title, title_size):
    fig = px.scatter_geo(agged_data, locations="Country", color=color, color_discrete_map=color_map, size="Head Count", locationmode="country names", size_max=size_max,)
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(
                size=title_size)))
    return fig


def chart_donut(agged_data, label_col, value_col, title, title_size, showlegend=False, **data_kwargs):
    fig = go.Figure(
        data=[go.Pie(
            labels=agged_data[label_col],
            values=agged_data[value_col],
            hole=0.4,
            **data_kwargs,
            textfont=dict(
                size=10),
            hovertemplate="%{label}<br>" + "Head Count=%{value}<br>" + "Pct=%{percent}" + "<extra></extra>",
            marker=dict(
                colors=agged_data["color"]))])
    fig.update_layout(
        height=550,
        uniformtext_minsize=11,
        uniformtext_mode="hide",
        showlegend=showlegend,
        title=dict(
            text=title,
            font=dict(size=title_size))
    )
    return fig


def chart_h_stacked_bars(agged_data, df_values, stacked_col, xcol, ycol, orientation, color_map, height, title, title_size):
    fig = go.Figure()
    if orientation == "h":
        hovertemplate = "%{text}=%{x}<extra></extra>"
    else:
        hovertemplate = "%{text}=%{y}<extra></extra>"
    for i in range(len(df_values[stacked_col])):
        nm = df_values[stacked_col][i]
        df_ = agged_data[agged_data[stacked_col] == nm]
        fig.add_trace(go.Bar(
            y=df_[ycol],
            x=df_[xcol],
            name=nm,
            text=df_[stacked_col],
            textposition="none",
            hovertemplate=hovertemplate,
            marker=dict(color=color_map[nm]),
            orientation=orientation
        ))
    fig.update_layout(
        barmode="stack",
        height=height,
        yaxis=dict(
            categoryorder="category descending",
            title=None),
        title=dict(
            text=title,
            font=dict(size=title_size))
    )
    return fig


def chart_scatter_programs(agged_data, unique_vals, colors, title_size, title):
    fig = go.Figure()
    for i in range(len(unique_vals)):
        prg = unique_vals[i]
        df_sub = agged_data[agged_data["Program Name"] == prg]
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
                color=colors[i])))
    fig.update_layout(
        height=600,
        xaxis=dict(title="Head Count"),
        yaxis=dict(title="FTE Contribution"),
        legend=dict(itemsizing="constant"),
        title=dict(
            text=title,
            font=dict(size=title_size))
    )
    return fig


# Specifics
# # Level Distro Waffle
def data_level_distro_waffle(df, color_map):
    mlevel_sort = df.groupby(["Level", "Manual Level"]).size().rename("Count").reset_index()
    mlevel_sort["group"] = mlevel_sort["Level"].apply(lambda x: x[0])
    mlevel_sort = mlevel_sort.sort_values(["group", "Level", "Manual Level"], ascending=[True, False, True])
    mlevel_grp_dict = pd.DataFrame(mlevel_sort["Manual Level"].unique()).rename(columns={0: "mlevel"}).reset_index()
    mlevel_grp_dict = dict(zip(mlevel_grp_dict["mlevel"], mlevel_grp_dict["index"]))
    mlevel_sort = mlevel_sort.groupby(["Manual Level"])["Count"].sum().rename("Count").reset_index().reset_index(drop=True)
    mlevel_sort["order"] = mlevel_sort["Manual Level"].map(mlevel_grp_dict)
    mlevel_sort["color"] = mlevel_sort["Manual Level"].map(color_map)
    mlevel_sort = mlevel_sort.sort_values("order").reset_index(drop=True)
    mlevel_sum = mlevel_sort["Count"].sum()
    labels = list(zip(mlevel_sort["Manual Level"], mlevel_sort["Count"]))
    labels = [f"{i[0]}: {i[1]} ({round(i[1] / mlevel_sum * 100, 2)}%)" for i in labels]
    return mlevel_sort, labels


def chart_level_distro_waffle(mlevel_sort, labels):
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
            framealpha=0))
    return fig

