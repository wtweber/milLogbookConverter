from fnmatch import fnmatch
import os

def getFILES(folder = os.getcwd(), pattern = "*.pdf"):
    list = []
    for path, subdirs, files in os.walk(folder):
        for name in files:
            if fnmatch(name, pattern):
                list.append(os.path.join(path, name))
    return list

def clean_pd(panda):

    panda = panda.dropna(axis=1, how='all')
    panda = panda.dropna(axis=0, how='all')
    panda = panda.reset_index(drop=True)
    panda.columns = panda.iloc[0]
    panda = panda.drop(panda.index[0])

    return panda

def isSolo(crew):
    if crew.shape[0] == 1:
        return True
    return False

def split_fp(flight_path = ['ZZZZ', 'ZZZZ']):
    seperator = ", "
    dash = "-"
    if flight_path == ['ZZZZ', 'ZZZZ']:
        return {'From':"", 'To': "", 'Route': ""}
    else:
        route_str = seperator.join(flight_path[1:len(flight_path)-1])
        #for i in range(1, flight_path.len()-1):
        return {'From':flight_path[0], 'To': flight_path[-1], 'Route': dash.join(flight_path)}
def INTERGER(s):
    try:
        return int(s)
    except:
        return 0
