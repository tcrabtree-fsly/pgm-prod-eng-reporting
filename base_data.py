from google.oauth2 import service_account
from googleapiclient import discovery
import string
import streamlit as st
import pandas as pd
import funcs as f
import webcolors


creds = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        # "https://www.googleapis.com/auth/drive""
    ],
)
service = discovery.build("sheets", "v4", credentials=creds)


def get_data(spreadsheet_id, range_name):
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=range_name).execute()
    rows = result.get("values", {})
    return rows


def frame_data(spreadsheet_id, range_name):
    rows = get_data(spreadsheet_id, range_name)
    df = pd.DataFrame(rows[1:], columns=rows[0])
    return df


def sheet_import_raw_data():
    spreadsheet_id = "103Smj1EpX2EjWUUjIORigAtMeiG4JS0v1Cb4dwXMbpI"
    range_name = "Data20220228!A4:Y359"
    data = frame_data(spreadsheet_id, range_name)
    return data


def sheet_people_data(data):
    return data.iloc[:, :15]


def sheet_status_data(data):
    status = data.iloc[:, :1].merge(data.iloc[:, 15:], left_index=True, right_index=True)
    status = status.drop(columns=["22-Q1ProgramTot", "22-Q2ProgramTot"])
    return status


st.cache(ttl=600)


def prep_data(spreadsheet_id, main_range, program_range):
    data = frame_data(spreadsheet_id, main_range)
    data["Employee Number"] = "id-" + data["Employee Number"].astype(str)
    staff = sheet_people_data(data)
    status = sheet_status_data(data)

    programs = frame_data(spreadsheet_id, program_range)
    programs = f.split_product_program(programs)
    long_status = f.sheet_prep_status_data(status, programs)
    long_status = long_status.sort_values(["Employee Number", "Quarter", "Program"]).reset_index(drop=True)

    df = staff.merge(long_status, how="left", on="Employee Number")
    df = f.swap_product_program(df)
    unstacked = f.unstack_data(df)

    df_values = f.unique_values_in_column(df)
    return df, unstacked, df_values


def write_to_sheet(df, spreadsheet_id, range_):
    value_input_option = "USER_ENTERED"
    data = [df.columns.values.tolist()]
    data.extend(df.values.tolist())
    value_range_body = {"values": data}
    request = service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, range=range_, valueInputOption=value_input_option, body=value_range_body)
    return request


def write_formatted_data(df, spreadsheet_id, sheet_name):
    alpha = list(string.ascii_uppercase)
    start_col = alpha[0]
    end_col = alpha[len(df.columns)]
    formatted_data_range = f"{sheet_name}!{start_col}:{end_col}"
    request = write_to_sheet(df, spreadsheet_id, formatted_data_range)
    return request.execute()


def change_shade(value, factor):
    return value * factor


def redistribute_rgb(r, g, b):
    threshold = 255.999
    m = max(r, g, b)
    if m <= threshold:
        return int(r), int(g), int(b)
    total = r + g + b
    if total >= 3 * threshold:
        return int(threshold), int(threshold), int(threshold)
    x = (3 * threshold - total) / (3 * m - total)
    gray = threshold - x * m
    return int(gray + x * r), int(gray + x * g), int(gray + x * b)


def rgb_to_hex(r, g, b):
    hexed_values = []
    for i in (r, g, b):
        v = "{:X}".format(i)
        if len(v) == 1:
            v = "0" + v
        hexed_values.extend(v)
    hex_color = "#" + "".join(hexed_values)
    return hex_color


def adjust_palette(hex_palette, change_factor):
    adjusted_palette = []
    for color in hex_palette:
        r, g, b = webcolors.hex_to_rgb(color)
        r = change_shade(r, change_factor)
        g = change_shade(g, change_factor)
        b = change_shade(b, change_factor)
        changed_color = redistribute_rgb(r, g, b)
        hex_color = rgb_to_hex(changed_color[0], changed_color[1], changed_color[2])
        adjusted_palette.append(hex_color)
    return adjusted_palette


# Colors
lighter_palette = ["#FFE4F4", "#FFEBEB", "#FFF1DD", "#E4FFF4", "#E6F8FC", "#C4CCD3", "#ffe9f5"]
light_palette = ["#D6799A", "#FF8487", "#FCD293", "#7AF7D1", "#71D3EC", "#AAB4BD", "#ffa9d6"]
medium_palette = ["#AF3354", "#FF282D", "#FCA119", "#23E0A8", "#04B2E1", "#7A848D", "#ff53ad"]
dark_palette = ["#8B134D", "#C20105", "#AD5309", "#007A60", "#00759C", "#434E58", "#cf006c"]
darker_palette = ["#471438", "#850003", "#723216", "#004735", "#003842", "#2D3741", "#3b001f"]

base_palette = medium_palette + light_palette + dark_palette + darker_palette
alt2palette = []
for i in range(len(light_palette)):
    alt2palette.append(medium_palette[i])
    alt2palette.append(light_palette[i])
alt4palette = []
alt4palette.extend(alt2palette)
for i in range(len(light_palette)):
    alt4palette.append(dark_palette[i])
    alt4palette.append(medium_palette[i])

# Get prepped data
spreadsheet_id = "152aO_kFgqNLcyeVfo4RvVHjKCVYjD5bWEhQ_YpCS9wU"
main_range = "Data20220228!A4:Y359"
program_range = "' 2022-Q1 ACTIVE Programs'!A2:E87"

df, unstacked, df_values = prep_data(spreadsheet_id, main_range, program_range)
