import pandas as pd
from msharp import msharp
from tims import tims
from CNAFenums import Approach, Landing, Role, Hours
import numpy as np
import os



def main():
    file_loc = '/home/wtweber/Documents/logBookFiles'
    msharp_file = 'msharp/AirCrewLogBook.xlsx'
    tims_file = 'tims/IndividualFlightHours_wizard.xlsx'
    tims_navflirs = 'tims/Navflirs'
    #tims_navflirs = "/home/wtweber/github/flight_logs/Navflirs"
    Aircraft = ['KC-130J']

    msharp_data = msharp(os.path.join(file_loc, msharp_file), aircraft_filter = Aircraft, nav = True)
    tims_data = tims(os.path.join(file_loc,tims_file),  nav_folder = None , EDIPI="1296076264")
    #output_data = mil2civ(msharp_data)
    output_data = mil2civ(msharp_data.append(tims_data, ignore_index=True, sort=False))

    print(returnCSV(output_data, file_loc))


def mil2civ(df=pd.DataFrame()):
    ######################################
    ##         Sum all approaches       ##
    ######################################
    Approaches = df.filter(items=(list(Approach.__members__)))
    df["Approaches"] = Approaches.sum(axis=1)

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

if __name__ == "__main__":
    main()
