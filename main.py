import pandas as pd
from msharp import msharp
from tims import tims
from CNAFenums import Approach, Landing, Role, Hours, AC_Type
import numpy as np
import os, sys, json
from progress.bar import Bar
from progress.spinner import Spinner
from distutils.util import strtobool


def main():
    #Load the options file
    options_file = ""
    bool_options = ["msharp_nav", "tims_nav"]
    for var in sys.argv[1:]:
        if "options" in var:
            options_file = var.split("=")[-1]

    if options_file:
        with open(options_file) as f:
            options = json.load(f)
    else:
        options = {}
    #print(options)

    #validate the options file
    for item in bool_options:
        if item in options.keys():
            options[item] = bool(strtobool(options[item]))# = strtobool(options["msharp_nav"])
        else:
            options[item] = False

    if "wd" not in options.keys():
        options["wd"] = os.getcwd()

    #print(options)

    #file_loc = '/home/wtweber/Documents/logBookFiles'
    #msharp_file = 'msharp/AirCrewLogBook.xlsx'
    #tims_file = 'tims/IndividualFlightHours_wizard.xlsx'
    #tims_navflirs = 'tims/Navflirs'
    #tims_navflirs = "/home/wtweber/github/flight_logs/Navflirs"
    Aircraft = ['KC-130J']


    #spinner = Spinner('Loading ')
    if "msharp_file" in options.keys():
        print("Reading MSHARP data.")
        msharp_data = msharp(os.path.join(options["wd"], options["msharp_file"]), aircraft_filter = Aircraft, nav = options["msharp_nav"])
    else:
        msharp_data = pd.DataFrame()
    if "tims_file" in options.keys():
        print("Reading TIMS data.")
        tims_data = tims(os.path.join(options["wd"],options["tims_file"]),  nav = options["tims_nav"] , EDIPI="1296076264")
    else:
        tims_data = pd.DataFrame()
    #output_data = mil2civ(msharp_data)
    print("Convert to civilian data.")
    output_data = mil2civ(msharp_data.append(tims_data, ignore_index=True, sort=False))
    output_data = aircraft_type_data(output_data)
    print(returnCSV(AirlineLogbook(output_data, output = "Airline"), options["wd"]))



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

    ######################################
    ##   Convert Hours to CCX           ##
    ######################################
    df["CC"] = df.apply(lambda row: row["TPT"] if row["TPT"] >= .5  else np.nan , axis=1)

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

def AirlineLogbook(df=pd.DataFrame(),output = "All"):
    output_col = ["Date",
                  "Model",
                  "Device",
                  "Type",
                  "Route",
                  "TPT"]
    if output == "Airline":
        output_col += ["SEL",
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
    elif output == "Military":
        output_col += ["TPT",
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
    else:
        output_col += ["AC_Type"]
        for type in AC_Type:
            output_col += [type.name]
        output_col += ["Day_ldg", "Night_ldg"]
        for land in Landing:
            output_col += [land.name]
        output_col += ["Approaches"]
        for app in Approach:
            output_col += [app.name]
        for hour in Hours:
            output_col += [hour.name]

    #print(output_col)
    airline_df = pd.DataFrame(columns=output_col)
    airline_df = airline_df.append(df, ignore_index = True, sort = False)
    if output != "All":
        airline_df = airline_df.iloc[:,0:len(output_col)]
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

    for ac in AC_Type:
        df[ac.name] = df.apply(lambda row: row["TPT"] if AC_Type[row["AC_Type"]] == ac  else np.nan , axis=1)

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
