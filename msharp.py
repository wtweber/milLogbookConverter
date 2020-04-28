import pandas as pd
import tabula
import numpy as np
from CNAFenums import Approach, Landing, Role
from local_func import getFILES
import uuid, re, os, glob
import PyPDF2
from progress.bar import Bar

def msharp(log_file, aircraft_filter='All', nav = False):
    print(log_file)
    msharp_data_raw = pd.read_excel(log_file, index_col=None)
    Column_type = msharp_data_raw.iloc[4]
    Landings_start = pd.Index(Column_type).get_loc('Landings')
    App_start = pd.Index(Column_type).get_loc('App')

    msharp_data_raw.iat[5,2] = "Date"

    #Trim off header data
    msharp_data = msharp_data_raw[7:msharp_data_raw.loc[msharp_data_raw.iloc[:,2] == 'Career Totals'].index.values[0]]

    msharp_data.columns = msharp_data_raw.iloc[5].fillna('DROP')
    msharp_data.loc[0,msharp_data.columns[Landings_start]] = "Landings"
    msharp_data.loc[0,msharp_data.columns[App_start]] = "App"
    msharp_data = msharp_data.sort_index()

    msharp_data = msharp_data.drop('DROP', axis=1)
    msharp_data.columns = msharp_data.columns.astype(str)


    new_app = pd.Index(msharp_data.iloc[0]).get_loc('App')
    new_ldg = pd.Index(msharp_data.iloc[0]).get_loc('Landings')
    msharp_data = msharp_data.drop(0)
    msharp_data = msharp_data.reset_index(drop=True)

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
    app_raw = msharp_data.iloc[:,new_app:-2]
    msharp_data = msharp_data.drop(columns=app_raw.columns)
    app_raw.columns = [x[0] for x in app_raw.columns]
    app_raw.columns = [Approach(x).name for x in app_raw.columns]

    ###############################################
    ##               Clean LDG                   ##
    ###############################################
    ldg_raw = msharp_data.iloc[:,new_ldg:-2]
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
    msharp_data = msharp_data.rename(columns={"TMS": "Model", "ACT": "AIT", "NAVFLIR":"Record", 6.0:""})

    msharp_data["Record"] = msharp_data["Record"].apply(lambda x: str(uuid.uuid4())[:8] if pd.isna(x) else x)
    msharp_data["Sorties"] = 1

    ###############################################
    ##          Read in Navflir Data             ##
    ###############################################
    if nav:
        data = {}
        msharp_data = msharp_data.assign(Origin = np.nan, Destination = np.nan, Route = np.nan)
        nav_folder = os.path.join(os.path.dirname(log_file), "NAVFLIRS")
        files = getFILES(folder = nav_folder)
        bar = Bar(nav_folder+":", max=len(files))
        for file in files:
            bar.next()
            pdfFileObj = open(file, 'rb')
            pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
            pageObj = pdfReader.getPage(0)

            recordID = pageObj.extractText().split('\n')[-6]
            pdf_data = tabula.read_pdf(file, multiple_tables=True, pages='all', lattice = True, silent = True)

            recordIndex = msharp_data.index[msharp_data['Record'] == recordID].tolist()
            route_data = pdf_data[2].iloc[2:].reset_index(drop = True)
            route_data.columns = pdf_data[2].iloc[1]
            for i in range(1,len(route_data.index),2):
                route_data.iloc[i] = route_data.iloc[i].shift(1)
            origin = route_data.iloc[0, route_data.columns.get_loc('ICAO OR SHIP\rI.D.')]
            destination = route_data.iloc[-1, route_data.columns.get_loc('ICAO OR SHIP\rI.D.')]
            route_list = route_data.iloc[1::2, route_data.columns.get_loc('ICAO OR SHIP\rI.D.')].tolist()
            route_list.insert(0,origin)
            route = " - ".join(route_list)

            msharp_data.iloc[recordIndex, msharp_data.columns.get_loc('Origin')] = origin
            msharp_data.iloc[recordIndex, msharp_data.columns.get_loc('Destination')] = destination
            msharp_data.iloc[recordIndex, msharp_data.columns.get_loc('Route')] = route
        bar.finish()
    #print(msharp_data)

    ###############################################
    ##               Filter Aircraft             ##
    ###############################################
    if aircraft_filter == 'All':
        return msharp_data
    else:
        return msharp_data[msharp_data.Model.isin(aircraft_filter)].reset_index(drop=True)
