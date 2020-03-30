import pandas as pd
import tabula
import numpy as np
from CNAFenums import Approach, Landing, Role
import uuid, re
from datetime import datetime
from local_func import getFILES, clean_pd, isSolo, split_fp
from progress.bar import Bar


def tims(log_file, nav_folder = None, aircraft_filter='All', EDIPI = "0000000000"):
    wing_date = "10/02/2012"
    edipi_str = 'xxxxxx'+EDIPI[-4:]
    print(edipi_str)

    ###############################################
    ##             Clean input                   ##
    ###############################################
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
    ##               Clean Apps/Ldgs             ##
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
    data = data.drop(['Apps', 'Event', 'Lnds', 'TFT', 'Side #'], axis=1)

    #Convert date field to datetime
    data["Date"] = data["Date"].apply(lambda x: datetime.strptime(x, "%m/%d/%Y %H:%M"))

    #Set role baised off hours and date
    data["Role"] = data.apply(lambda row: Role.INSTRUCTOR.name if row["IPT"] > 0.0 else (Role.COPILOT.name if row["Date"] > datetime.strptime(wing_date, "%d/%m/%Y") else Role.STUDENT_PILOT.name) , axis=1)
    #Split date a Time
    data["Time"] = data["Date"].apply(lambda x:  x.strftime('%H:%M'))
    #data["Date"] = data["Date"].apply(lambda x:  x.strftime('%d/%m/%Y'))
    #Set type based off model name
    data["Type"] = data["Model"].apply(lambda x: "Aircraft" if x.startswith("T") else "Simulator")
    #rename columns to match
    data = data.rename(columns={"Bureau #": "Device", "Document Number": "Record", "# Sorties": "Sorties"})

    ###############################################
    ##              read navflirs                ##
    ###############################################
    if nav_folder != None:
        files = getFILES(folder = nav_folder)
        bar = Bar('NAVFLIRS:', max=len(files))
        for file in files:
            pdf_data = tabula.read_pdf(file, multiple_tables=True, pages='all', lattice = True, silent = True)[0]
            admin_index = 0#pdf_data.index[pdf_data.loc[:, 0]=='Admin'].tolist()#[0]
            sorties_index = pdf_data.index[pdf_data["Admin"] == 'Sorties'].tolist()[0]
            logistics_index = pdf_data.index[pdf_data["Admin"] == 'Logistics'].tolist()[0]
            aircrew_index = pdf_data.index[pdf_data["Admin"] == 'Aircrew'].tolist()[0]
            tactical_index = pdf_data.index[pdf_data["Admin"] == 'Tactical'].tolist()[0]
            training_index = pdf_data.index[pdf_data["Admin"] == 'Training'].tolist()[0]
            activities_index = pdf_data.index[pdf_data["Admin"] == 'Activities'].tolist()[0]
            engine_index = pdf_data.index[pdf_data["Admin"] == 'Engines'].tolist()[0]

            Admin = clean_pd(pdf_data.loc[admin_index:sorties_index-1, :])
            Sorties = clean_pd(pdf_data.loc[sorties_index+1:logistics_index-1, :])
            Aircrew = clean_pd(pdf_data.loc[aircrew_index+1:tactical_index-1, :])
            Activities = clean_pd(pdf_data.loc[activities_index+1:engine_index-1, :])
            Training = clean_pd(pdf_data.loc[training_index+1:activities_index-1, :])

            #find me
            me = Aircrew.loc[Aircrew.loc[:, 'EDIPI'] == edipi_str, :]
            if len(me) == 0:
                print("didnt find you.")
            else:
                matched_index = data.loc[data['Record'] == Admin.at[1, 'Document']].index.values
                if len(matched_index) == 1:
                    #print("Matched a record.")
                    data.at[matched_index[0], "Role"] = Role(me["Role"].values[0]).name
                    stops = []
                    for index, leg in Sorties.iterrows():
                        if index == 1:
                            stops.append(leg["Departure ICAO"])
                        stops.append(leg["Arrival ICAO"])
                    #flights.at[matched_index[0], "Origin"] = stops[0]
                    #flights.at[matched_index[0], "Destination"] = stops[-1]

                    #if len(stops) > 2:
                    #    flights.at[matched_index[0], "Route"] = stops[1:-1]
                    legs_dict = split_fp(stops)
                    data.at[matched_index[0], "Route of Flight"] = legs_dict["Route of Flight"]
                    if isSolo(Aircrew):
                        data.at[matched_index[0], "Solo"] = data.at[matched_index[0], "TPT"]
                    else:
                        data.at[matched_index[0], "Solo"] = np.nan

                    #print(Training.index[Training.iloc[:, 3]=='xxxxxx6264'].tolist())

                    #me_training = Training.loc[Training.loc[:, 'SSN/EDIPI'] == 'xxxxxx6264', :]
                    T_R = []
                    others = []
                    for index, line in Training.iterrows():
                        #print()
                        if line.loc["SSN/EDIPI"].values[0] == "xxxxxx6264":
                            if line["Event"] != "None":
                                T_R.append(line["Event"])
                        else:
                            others.append("%s for %s"%( line["Event"], line["Person Receiving Event"]))
                    data.at[matched_index[0], "TR"] = T_R
                    #print(flights.dtypes)
                elif len(matched_index) > 1:
                    print("ERROR FOUND MULTIPLE MATCHING RECORDS: %s"%Admin.at[1, 'Document'])
                else:
                    print("NO MATCH FOUND.")
            bar.next()
        bar.finish()

    return data
