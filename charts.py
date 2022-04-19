import pandas as pd
import re
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


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