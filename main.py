import pandas as pd
from msharp import msharp
from tims import tims
from CNAFenums import Approach, Landing, Role, Hours, AC_Type
import numpy as np
import os
from progress.bar import Bar


def main():
    load_nav = True
    file_loc = '/home/wtweber/Documents/logBookFiles'
    msharp_file = 'msharp/AirCrewLogBook.xlsx'
    tims_file = 'tims/IndividualFlightHours_wizard.xlsx'
    tims_navflirs = 'tims/Navflirs'
    #tims_navflirs = "/home/wtweber/github/flight_logs/Navflirs"
    Aircraft = ['KC-130J']

    msharp_data = msharp(os.path.join(file_loc, msharp_file), aircraft_filter = Aircraft, nav = load_nav)
    tims_data = tims(os.path.join(file_loc,tims_file),  nav = load_nav , EDIPI="1296076264")
    #output_data = mil2civ(msharp_data)
    output_data = mil2civ(msharp_data.append(tims_data, ignore_index=True, sort=False))

    output_data = aircraft_type_data(output_data)

    print(returnCSV(AirlineLogbook(output_data), file_loc))



def mil2civ(df=pd.DataFrame()):
    ######################################
    ##         Sum all approaches       ##
    ######################################
    Approaches = df.filter(items=(list(Approach.__members__)))
    for item in Approaches.columns:
        Approaches[item] = pd.to_numeric(Approaches[item])
    df["Approaches"] = Approaches.sum(axis=1)

    df = df.assign(Day_ldg = 0, Night_ldg = 0)
    Landings = df.filter(items=(list(Landing.__members__))).fillna(0)
    for item in Landings.columns:
        Landings[item] = pd.to_numeric(Landings[item])
        if Landing[item].LdgType == "Day":
            df["Day_ldg"] = df["Day_ldg"] + Landings[item]
        elif Landing[item].LdgType == "Night":
            df["Night_ldg"] = df["Night_ldg"] + Landings[item]
    #df["Day Ldg"] = df.apply(lamda row: )

    ######################################
    ##   Convert Hours to PIC/SIC       ##
    ######################################
    df["PIC"] = df.apply(lambda row: row["TPT"] if Role[row["Role"]].RoleType == "PIC"  else np.nan , axis=1)
    df["SIC"] = df.apply(lambda row: row["TPT"] if Role[row["Role"]].RoleType == "SIC"  else np.nan , axis=1)

    df = df.replace(0, np.nan)


    return df.sort_values(by='Date').reset_index(drop=True)

def returnCSV(df=pd.DataFrame(), path = os.getcwd()):
    writer = pd.ExcelWriter(os.path.join(path, 'Converted_Logbook.xlsx'), engine = 'xlsxwriter')
    df.to_excel(writer, index=False)
    writer.save()
    #df.to_csv ('msharp_navflir.csv', index = None, header=True)
    return 'Sucess'

def split_dates(df=pd.DataFrame()):
    df["Time"] = [d.time() for d in df['my_timestamp']]
    df["Date"] = [d.date() for d in df['my_timestamp']]

    return df

def AirlineLogbook(df=pd.DataFrame()):
    airline_output = ["Date",
                      "Model",
                      "Device",
                      "Type",
                      "Route",
                      "TPT",
                      "SEL",
                      "MEL",
                      "HEL",
                      "TILT",
                      "GLIDER",
                      "Day_ldg",
                      "Night_ldg",
                      "NIGHT",
                      "AIT",
                      "SIT",
                      "Approaches",
                      "CC",
                      "Solo",
                      "PIC",
                      "SIC",
                      "Dual",
                      "IPT",
                      "Sorties",
                      "SCT",
                      "CAT/JATO",
                      "Remarks"]
    airline_df = pd.DataFrame(columns=airline_output)
    airline_df = airline_df.append(df)
    airline_df = airline_df.iloc[:,0:len(airline_output)]
    return airline_df

def aircraft_type_data(df=pd.DataFrame()):
    bar = Bar('Matching aircraft types:', max=len(df.index))
    df = df.assign(AC_Type = np.nan)
    aircraft_data = pd.read_excel("aircraft.xlsx")
    error_matching = []
    for index, row in df.iterrows():
        bar.next()
        ac_Flown = row['Model']
        mask = aircraft_data['model_no'].values == ac_Flown
        matched_aircraft = aircraft_data[mask]
        num_found = len(matched_aircraft.index)
        if num_found == 1:
            df.iloc[index, df.columns.get_loc('AC_Type')] = process_ac_type(matched_aircraft.squeeze())#, matched_aircraft.columns.get_loc('aircraft_desc')]
        elif num_found < 1:
            trimmed_ac = ac_Flown
            while not trimmed_ac[-1].isdigit():
                trimmed_ac = trimmed_ac[:-1]
            mask = aircraft_data['model_no'].values == trimmed_ac
            matched_aircraft = aircraft_data[mask]
            num_found = len(matched_aircraft.index)
            if num_found < 1:
                if ac_Flown not in error_matching:
                    error_matching.append(ac_Flown)
            else:
                df.iloc[index, df.columns.get_loc('AC_Type')] = process_ac_type(matched_aircraft.squeeze())#matched_aircraft.iloc[0, matched_aircraft.columns.get_loc('aircraft_desc')]
        else:
            print("Multiple matches found for type: %s" %ac_Flown)
            print(matched_aircraft)
            print(matched_aircraft.iloc[0, matched_aircraft.columns.get_loc('model_name')])
    #print(aircraft_data)
    bar.finish()

    if len(error_matching):
        print("Error importing:")
        print(error_matching)

    return df

def process_ac_type(aircraft = pd.Series(dtype=object)):
    if aircraft.empty:
        return AC_Type.UNK.name
    if aircraft['aircraft_desc'] == 'LandPlane':
        if aircraft['engine_count'] > 1: return AC_Type.MEL.name
        else: return AC_Type.SEL.name
    elif aircraft['aircraft_desc'] in ['SeaPlane', 'Amphibious']:
        if aircraft['engine_count'] > 1: return AC_Type.MES.name
        else: return AC_Type.SES.name
    elif aircraft['aircraft_desc'] == 'Helicopter':
        return AC_Type.HEL.name

if __name__ == "__main__":
    main()
