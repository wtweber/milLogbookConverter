from enum import Enum, auto
import json
#from classes import hours, leg, flight

##################################################
##                                              ##
##                 ENUM DEFINITIONS             ##
##                                              ##
##################################################
class Role(Enum):
  ACFT_CMDR = 'A'
  OBSERVER = 'B'
  COPILOT = 'C'
  SAR_CREW = 'D'
  ECM = 'E'
  CREWCHIEF = 'F'
  FLIGHT_ATTENDANT = 'G'
  FLIGHT_SURGEON = 'H'
  INSTRUCTOR = 'I'
  SENSOR_OPERATOR = 'J'
  FLT_TECHNICIAN = 'K'
  LOADMASTER = 'L'
  STUDENT_PILOT = 'M'
  MISSION_SPECIALIST = 'N'
  ORDNANCE = 'O'
  NFO = 'P'
  COMMUNICATIONS = 'Q'
  RADAR = 'R'
  AC_MSN_CMDR = 'S'
  CREW_UNDER_TRAINING = 'T'
  NON_CREW_UNDER_TRAINING = 'U'
  OTHER = 'V'
  GUNNER = 'W'
  SECOND_MECH = 'X'
  HELO_UTILITY = 'Y'
  MSN_CMDR = 'Z'

  @property
  def RoleType(self):
      if self in [Role.ACFT_CMDR, Role.INSTRUCTOR, Role.AC_MSN_CMDR]:
          return "PIC"
      elif self in [Role.COPILOT, Role.STUDENT_PILOT, Role.MSN_CMDR]:
          return "SIC"
      else:
          return "SPC"

class tz_enum(Enum):
    A = 'Etc/GMT-1'
    B = 'Etc/GMT-2'
    C = 'Etc/GMT-3'
    D = 'Etc/GMT-4'
    E = 'Etc/GMT-5'
    F = 'Etc/GMT-6'
    G = 'Etc/GMT-7'
    H = 'Etc/GMT-8'
    I = 'Etc/GMT-9'
    K = 'Etc/GMT-10'
    L = 'Etc/GMT-11'
    M = 'Etc/GMT-12'
    N = 'Etc/GMT+1'
    O = 'Etc/GMT+2'
    P = 'Etc/GMT+3'
    Q = 'Etc/GMT+4'
    R = 'Etc/GMT+5'
    S = 'Etc/GMT+6'
    T = 'Etc/GMT+7'
    U = 'Etc/GMT+8'
    V = 'Etc/GMT+9'
    W = 'Etc/GMT+10'
    X = 'Etc/GMT+11'
    Y = 'Etc/GMT+12'
    Z = 'Etc/GMT'

class Landing(Enum):
    DayLdg = '6'
    NightLdg = 'F'
    NVGLdg = 'P'
    ShipArrest = '1'
    ShipT_G = '2'
    ShipBolter = '3'
    ShipHelio = '4'
    NFO = 'Y'
    FCLP = '5'
    FiledArrest = '7'
    VSTOLSlow = '8'
    VSTOLVert = '9'
    VSTOLVertRoll = '0'
    NightShipArrest = 'A'
    NightShipT_G = 'B'
    NightShipBolter = 'C'
    NightShipHelio = 'D'
    NightNFO = 'Z'
    NightFCLP = 'E'
    NightFiledArrest = 'G'
    NightVSTOLSlow = 'H'
    NightVSTOLVert = 'J'
    NightVSTOLVertRoll = 'K'
    NVGFDLP = 'Q'
    OTHER = '?'

class Approach(Enum):
    PA = '1'
    PS = 'A'
    NPA = '2'
    NPS = 'B'
    AA = '3'
    AS = 'C'
    ANVD = '4'
    OTHER = '?'

    def __str__(self):
        if self == Approach.PA:
            return "Precision Actual"
        elif self == Approach.PS:
            return "Precision Simulated"
        elif self == Approach.NPA:
            return "Nonprecision Actual"
        elif self == Approach.NPS:
            return "Nonprecision Simulated"
        elif self == Approach.AA:
            return "Auto Actual"
        elif self == Approach.AS:
            return "Auto Simulated"
        elif self == Approach.ANVD:
            return "Auto NVD"
        else:
            return "NONE"
    @property
    def AppType(self):
        if self in [Approach.PA, Approach.PS]:
            return "Precision"
        elif self in [Approach.NPA, Approach.NPS]:
            return "Nonrecision"
        elif self in [Approach.AA, Approach.AS]:
            return "Auto"
        else:
            return "Unknown"

class Hours(Enum):
    PIC = "Pilot in Command"
    SIC = "Second in Command"
    NT = "Night"
    AIT = "Actual Instrument"
    SIT = "Simulated Instrument"
    DualRcvd = "Dual Recieved"
    INS = "Instructor/Evaluator"
    NVG = "Night Vision Goggles"
    Combat = "Combat"
    HLL = "High Light Level"
    LLL = "Low Light Level"
    FWNVG = "Fixed Wing NVG"
    FPT = "First Pilot Time"
    CPT = "Co-Pilot Time"
    CMDR = "Aircraft Commander"
    SCT = "Special Crew Time"
    TR = "T&R Codes"


# class EnumEncoder(json.JSONEncoder):
#     def default(self, obj):
#         print(type(obj))
#         if type(obj) in PUBLIC_ENUMS.values():
#             print("ENUM~~~~~~~~~~~~~~~~~~")
#             return {"__enum__":str(obj)}
#         if type(obj) in ["legs", "hours", "flight"]:
#             return obj.toJSON()
#         #if type(obj) in ["flight"]:
#         #    return json.dumps(obj, default=lambda o: o.__dict__)
#         return json.JSONEncoder.default(self, obj)
#
# PUBLIC_ENUMS = {
#     'Role': Role,
#     # ...
# }
#
# PUBLIC_CLASSES = {
#     'flight': flight,
#     'leg': leg,
#     'hours': hours
# }
