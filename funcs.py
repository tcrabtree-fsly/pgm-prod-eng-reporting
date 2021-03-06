import pandas as pd
import re
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# This function needs to be revisited
def sheet_quarter_program_status_column(df, quarter_num, program_num, program_df, last=False):
    qp = df.iloc[:, :3].copy()
    qp["Quarter"] = quarter_num
    qp["Program"] = program_num
    qp.columns = ["Employee Number", "Program Name", "%", "Quarter", "Program"]
    qp["Product Line"] = qp["Program Name"].apply(lambda x: x.split(":")[0] if re.search(":", x) else None)
    qp["Program Name"] = qp["Program Name"].apply(lambda x: x.split(":")[1] if re.search(":", x) else x)
    qp = qp[["Employee Number", "Program Name", "Product Line", "%", "Quarter", "Program"]]
    qp = qp[qp["%"] != ""]
    qp = qp[qp["Program Name"] != ""]
    if last is True:
        df = df = df.iloc[:, :1].merge(df.iloc[:, 3:], left_index=True, right_index=True)
    else:
        pass
    return qp, df


# This function needs to be revisited
def sheet_parse_status_columns(df, program_df):
    q1p1, df = sheet_quarter_program_status_column(df, 1, 1, program_df, True)
    q1p2, df = sheet_quarter_program_status_column(df, 1, 2, program_df, True)
    q2p1, df = sheet_quarter_program_status_column(df, 2, 1, program_df, True)
    q2p2, df = sheet_quarter_program_status_column(df, 2, 2, program_df, False)
    long_form = pd.concat([q1p1, q1p2, q2p1, q2p2], ignore_index=True)
    return long_form


def sheet_prep_status_data(status, program_df):
    long_status = sheet_parse_status_columns(status, program_df)
    long_status["%"] = long_status["%"].apply(lambda x: re.sub(r"\%", "", x)).astype(int)
    long_status["%"] = long_status["%"] / 100
    return long_status


def split_product_program(programs):
    programs["Product Line"] = programs["Program Name"].apply(lambda x: x.split(":")[0] if re.search(":", x) else None)
    programs["Program Name"] = programs["Program Name"].apply(lambda x: x.split(":")[1] if re.search(":", x) else x)
    return programs


def swap_product_program(df):
    df["Product Line"] = df.apply(lambda row: row["Program Name"] if row["Product Line"] == "Other" else row["Product Line"], axis=1).str.strip()
    df["Program Name"] = df.apply(lambda row: "Other" if row["Product Line"] == row["Program Name"] else row["Program Name"], axis=1).str.strip()
    return df


# This function needs to be revisited
def unstack_data(df):
    unstacked = df.set_index(["Employee Number", "Quarter", "Program"]).unstack().reset_index()
    col_lvls = unstacked.columns.tolist()
    cols = []
    for c in col_lvls:
        if c[1] == "":
            cols.append(c[0])
        else:
            cols.append(c[0] + " " + str(c[1]))

    unstacked.columns = cols
    for i, c in enumerate(unstacked.columns[2:31]):
        if i % 2 != 0:
            unstacked = unstacked.drop(columns=[c])

    for c in unstacked.columns[:16]:
        if re.search(r"\d", c):
            splits = c.split(" ")[:-1]
            joined = " ".join(splits)
            unstacked.rename(columns={c: joined}, inplace=True)

    unstacked = unstacked[["Employee Number"] + unstacked.columns.tolist()[2:16] + ["Quarter", "Program Name 1", "Product Line 1", "Program Name 2", "Product Line 2", "% 1", "% 2"]].rename(columns={"% 1": "Program 1 %", "% 2": "Program 2 %"})
    na_cols = unstacked.columns[unstacked.isna().any()].tolist()
    for c in na_cols:
        if unstacked[c].dtype == object:
            unstacked[c] = unstacked[c].fillna("")
        else:
            unstacked[c] = unstacked[c].fillna(0)
    unstacked["Quarter"] = unstacked["Quarter"].astype(int)
    unstacked["Total %"] = unstacked["Program 1 %"] + unstacked["Program 2 %"]
    unstacked = unstacked.sort_values(by="Employee Number").reset_index(drop=True)
    return unstacked


def unique_values_in_column(df):
    unique_dict = {}
    for c in df.columns:
        v = df[c].unique().tolist()
        v.sort()
        unique_dict[c] = v
    return unique_dict


# This function needs to be revisited
def agg_data_count_fte(df, group_cols, sort_by_cols, color_col="Product Line", color_map=False, **kwargs):
    grouped = df.groupby(group_cols)[["Employee Number", "%"]].agg({"Employee Number": "nunique", "%": "sum"}).reset_index().rename(columns={"Employee Number": "Head Count", "%": "FTE Contribution"})
    grouped = grouped.sort_values(sort_by_cols, **kwargs)
    if color_map is not False:
        grouped["color"] = grouped[color_col].map(color_map)
    return grouped


def color_map(unique_vals, colors):
    color_mult = (len(unique_vals) + len(colors) - 1) // len(colors)
    colors_sub = colors * color_mult
    return dict(zip(unique_vals, colors_sub[:len(unique_vals)]))

