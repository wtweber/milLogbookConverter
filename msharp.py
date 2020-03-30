import pandas as pd
import tabula
import numpy as np
from CNAFenums import Approach, Landing, Role
import uuid, re

def msharp(log_file, aircraft_filter='All'):
    msharp_data_raw = pd.read_excel(log_file, index_col=None)
    #print(msharp_data_raw)
    Column_type = msharp_data_raw.iloc[4]
    #print(Column_type)
    Landings_start = pd.Index(Column_type).get_loc('Landings')
    App_start = pd.Index(Column_type).get_loc('App')


    msharp_data_raw.iat[5,2] = "Date"
    #print(msharp_data_raw)
    msharp_data = msharp_data_raw[7:msharp_data_raw.loc[msharp_data_raw.iloc[:,2] == 'Career Totals'].index.values[0]]

    msharp_data.columns = msharp_data_raw.iloc[5].fillna('DROP')
    #print(msharp_data)
    msharp_data = msharp_data.drop('DROP', axis=1)
    msharp_data.columns = msharp_data.columns.astype(str)
    msharp_data = msharp_data.reset_index(drop=True)

    #print(msharp_data)

    #career = msharp_data.loc[msharp_data['Date'] == 'Career Totals']
    #print(career.index.values)


    ###############################################
    ##               Clean T&R                   ##
    ###############################################
    TR = msharp_data.filter(regex=("T&R*"))
    msharp_data = msharp_data.drop(columns=TR.columns)
    TR_string = []
    for index, row in TR.iterrows():
        row = row.dropna()
        row = row.astype(str)
        TR_string.append(row.str.cat(sep=', '))
    msharp_data['T&R']=TR_string

    ###############################################
    ##               Clean APP                   ##
    ###############################################
    app_raw = msharp_data.iloc[:,App_start-1:-1]
    msharp_data = msharp_data.drop(columns=app_raw.columns)
    app_raw.columns = [x[0] for x in app_raw.columns]
    app_raw.columns = [Approach(x).name for x in app_raw.columns]

    ###############################################
    ##               Clean LDG                   ##
    ###############################################
    ldg_raw = msharp_data.iloc[:,Landings_start-1:-1]
    msharp_data = msharp_data.drop(columns=ldg_raw.columns)
    ldg_raw.columns = [x[0] for x in ldg_raw.columns]
    ldg_raw.columns = [Landing(x).name for x in ldg_raw.columns]
    msharp_data = pd.concat([msharp_data, app_raw, ldg_raw], axis=1)

    ###############################################
    ##               Clean Date                  ##
    ###############################################
    #msharp_data["Date"] = msharp_data["Date"].apply(lambda x: x.strftime('%d/%m/%Y'))

    ###############################################
    ##               Add role                    ##
    ###############################################
    msharp_data["Role"] = msharp_data.apply(lambda row: Role.ACFT_CMDR.name if row["ACMDR"] > 0.0 else (Role.COPILOT.name if row["TPT"] > 0.0 else Role.OTHER.name) , axis=1)
    msharp_data = msharp_data.rename(columns={"TMS": "Model", "ACT": "AIT", "NAVFLIR":"Record"})

    msharp_data["Record"] = msharp_data["Record"].apply(lambda x: str(uuid.uuid4())[:8] if pd.isna(x) else x)
    msharp_data["Sorties"] = 1
    ###############################################
    ##               Filter Aircraft             ##
    ###############################################
    if aircraft_filter == 'All':
        return msharp_data
    else:
        return msharp_data[msharp_data.Model.isin(aircraft_filter)].reset_index(drop=True)
