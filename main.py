import pandas as pd
from msharp import msharp
from tims import tims
from CNAFenums import Approach, Landing, Role, Hours
import numpy as np

def main():
    msharp_file = '/home/wtweber/github/flight_logs/MSHARP2.0 AirCrewLogBook.xlsx'
    tims_file = '/home/wtweber/github/flight_logs/IndividualFlightHours_wizard.xlsx'
    Aircraft = ['KC-130J']

    data = msharp(msharp_file, Aircraft)

    print(mil2civ(data))

    tims(tims_file)


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


    return df

if __name__ == "__main__":
    main()
