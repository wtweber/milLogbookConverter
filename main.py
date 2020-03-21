import pandas as pd
from msharp import msharp
from tims import tims
from CNAFenums import Approach, Landing, Role, Hours
import numpy as np



def main():
    msharp_file = '/home/wtweber/github/flight_logs/MSHARP2.0 AirCrewLogBook.xlsx'
    tims_file = '/home/wtweber/Desktop/IndividualFlightHours_wizard.xlsx'
    tims_navflirs = '/home/wtweber/github/flight_logs/Processed files/Navflirs'
    #tims_navflirs = "/home/wtweber/github/flight_logs/Navflirs"
    Aircraft = ['KC-130J']

    msharp_data = msharp(msharp_file, Aircraft)
    tims_data = tims(tims_file,  nav_folder = tims_navflirs, EDIPI="1296076264")

    output_data = mil2civ(msharp_data.append(tims_data, ignore_index=True, sort=False))

    print(output_data)


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


    return df.sort_values(by='Date').reset_index(drop=True)




if __name__ == "__main__":
    main()
