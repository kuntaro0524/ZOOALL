import sqlite3, csv, os, sys
import ESA

class ESAcheck():
    def __init__(self, dbname):
        self.dbname = dbname
        self.n_cur=0

        # Wavelength limit
        self.w_min=0.70000
        self.w_max=1.30000

    def getRequiredInformation(self,each_dict):
        puck_id=p['puckid']
        puck_id=p['pinid']

    def checkDB(self):
        self.esa = ESA.ESA(self.dbname)
        self.cond_dict = self.esa.getDict()

        self.puck_id_list=[]
        self.pin_id_list=[]

        for p in self.cond_dict:
            # Puck ID & pin ID
            puck_id=p['puckid']
            self.puck_id_list.append(p['puckid'])
            self.pin_id_list.append(p['pinid'])

        print self.puck_id_list
        print self.pin_id_list

        return self.cond_dict

if __name__=="__main__":

    e = ESAcheck(sys.argv[1])
    e.getConditionsFromDB()
