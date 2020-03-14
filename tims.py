import pandas as pd
import tabula
import numpy as np
from CNAFenums import Approach, Landing, Role
import uuid, re
from datetime import datetime

def tims(log_file, aircraft_filter='All'):
    data_raw = pd.read_excel(log_file, index_col=None)
    data = data_raw[5:]

    data.columns = data_raw.iloc[4].fillna('DROP')
    data = data[data.Date != "Date"]
    data = data[data.Date != "Period Totals:"]
    data = data.dropna(how='all')
    data = data.reset_index(drop=True)

    ###############################################
    ##     Clean comments and drop empty rows    ##
    ###############################################
    for index, row in data.iterrows():
        if not pd.isna(row["Event"]):
            row["Remarks"] = "-".join([str(row["Event"]), str(row["Remarks"])])
        if pd.isna(row["Date"]):
            data.iat[index-1,-1] = ", ".join([str(data.iat[index-1,-1]), str(row["Remarks"])])
    data = data.dropna(subset = ["Date"])
    data = data.reset_index(drop=True)

    ###############################################
    ##               Clean Apps                  ##
    ###############################################
    add_df = pd.DataFrame()
    #for name, member in Approach.__members__.items():
    #    app_df[name] = np.nan
    for index, row in data.iterrows():
        Add_series = pd.Series()
        if not pd.isna(row["Apps"]):
            approaches = re.split(' ', str(row["Apps"]))
            for a in approaches:
                Add_series[Approach(a[0]).name] = a[-1]
        if not pd.isna(row["Lnds"]):
            #print(row["Lnds"])
            ldgs = re.split(' ', str(row["Lnds"]))
            for l in ldgs:
                lan = l.split("/")
                Add_series[Landing(lan[0]).name] = lan[1]
        add_df = add_df.append(Add_series, ignore_index=True)
    data = pd.concat([data, add_df], axis=1)
    data = data.drop(['Apps', 'Event', 'Lnds'], axis=1)

    data["Date"] = data["Date"].apply(lambda x: datetime.strptime(x, "%m/%d/%Y %H:%M"))

    data["Role"] = data.apply(lambda row: Role.ACFT_CMDR.name if row["IPT"] > 0.0 else (Role.COPILOT.name if row["Date"] > datetime.strptime("10/02/2012", "%d/%m/%Y") else Role.STUDENT_PILOT.name) , axis=1)
    data["Time"] = data["Date"].apply(lambda x:  x.strftime('%H:%M'))
    data["Date"] = data["Date"].apply(lambda x:  x.strftime('%d/%m/%Y'))
    data["Type"] = data["Model"].apply(lambda x: "Aircraft" if x.startswith("T") else "Simulator")



    print(data)
