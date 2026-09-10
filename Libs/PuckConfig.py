import os,sys
import numpy as np
import pandas as pd

class PuckConfig():
    def __init__(self, configfile):
        self.configfile=configfile
        self.isRead=False

    def readConfig(self):
        # Pandas read csv
        self.df = pd.read_csv(self.configfile)
        print(self.df)
        self.df.head()

        def reprep(row_data):
            lowstr=row_data.lower()
            if lowstr.rfind("h")!=-1:
                value=float(lowstr.replace("h",""))
                return(value)
            elif lowstr.rfind("s")!=-1:
                value=float(lowstr.replace("s",""))
                return(value*8.0)
            elif lowstr.rfind("m")!=-1:
                value=float(lowstr.replace("m",""))
                return(value/60.0)

        # Condition 
        self.df['time_limit_hour'] = self.df['time_limit'].apply(reprep)

        # Dataframe to Dictionary
        self.puck_dict = self.df.to_dict(orient='records')
        # Remove space from the line string
        self.isRead=True
        return self.puck_dict
    
if __name__ == "__main__":
    pc=PuckConfig(sys.argv[1])
    pi=pc.readConfig()
    print(pi)
    for pi in pi:
        print(pi)