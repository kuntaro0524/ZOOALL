# -*- coding: utf-8 -*-
from Libs import MyException
import sys,os
from configparser import ConfigParser, ExtendedInterpolation

class BSSconfig:
    def __init__(self):
        #self.confile = config_file
        self.isRead = False
        self.isPrepDict = False
        self.isPrep = False

        # BL32XU setting
        # beamline.ini から bssconfig_file のパスを読む
        # section: files, option: bssconfig_file
        self.inifile_path = "%s/beamline.ini" % os.environ['ZOOCONFIGPATH']
        self.blini = ConfigParser(interpolation=ExtendedInterpolation())
        self.blini.read(self.inifile_path)
        self.confile = self.blini.get("files", "bssconfig_file")
        print(self.confile)

        # camera.inf
        self.camerainf_path = self.blini.get("files", "camera_inf")

        self.isRead = False
        self.isPrep = False
        self.debug = False

    def storeLines(self):
        ifile = open(self.confile, "r")
        self.lines = ifile.readlines()

        ifile.close()
        self.isRead = True

    def is_integer(self, number):
        try:
            float(number)
        except ValueError:
            return False
        else:
            return float(number).is_integer()

    def getPulse4MinZoomRatio(self):
        self.zoom_info = self.readZoomOption()

        # zoom_info は [(zoom1, pulse1), (zoom2, pulse2), ...] という形式
        # zoom? は float, pulse? は int
        # This function finds the minimum zoom ratio and return the pulse value
        # for the minimum zoom ratio
        min_zoom = 9999999.999999
        return_pulse = 9999999
        for zoom, pulse in self.zoom_info:
            if zoom < min_zoom:
                min_zoom = zoom
                return_pulse = pulse

        print("Minimum zoom ratio is %s" % min_zoom)
        
        return return_pulse

    def readZoomOption(self):
        if self.isRead == False: self.storeLines();
        # camera.inf is read
        self.zoom_value = []
        tlines = open(self.camerainf_path, "r").readlines()
        for line in tlines:
            if "ZoomOptions1:" in line and line.startswith("#")==False:
                print(line)
                value_bunch = line.split(":")[1]
                for column in value_bunch.split(): 
                    value = float(column)
                    self.zoom_value.append(value)
        self.zoom_pulses = []
        for line in self.lines:
            line=line.strip()
            if "Microscope_Zoom_Options:" in line and line.startswith("#")==False:
                print(line)
                value_bunch = line.split(":")[1]
                if self.debug:
                    print(value_bunch)
                for column in value_bunch.split():
                    # confirm 'column' is integer or not
                    if self.is_integer(column) == False:
                        continue
                    value = float(column)
                    self.zoom_pulses.append(value)

        self.zoom_info=[]
        for zoom,pulse in zip(self.zoom_value, self.zoom_pulses):
            print(zoom,pulse)
            self.zoom_info.append((zoom,pulse))

        return self.zoom_info

    def getBLobject(self):
        if self.isRead == False: self.storeLines()
        for line in self.lines:
            line=line.strip()
            if "BL_Object" in line:
                self.beamline = line.split(":")[1]
                return self.beamline

    # bss.config を読んで各軸の情報を辞書として格納するテスト
    def storeAxesBlocks(self):
        if self.isRead == False:
            self.storeLines()
        
        inBlock=False
        axesBlocks=[]
        blockLines=[]
        for line in self.lines:
            line = line.strip()
            if "_axis_begin" in line:
                inBlock=True
                # print("Start")
                continue
            if inBlock==True and "_axis_end" in line:
                axesBlocks.append(blockLines)
                blockLines=[]
                inBlock=False
                continue
            if inBlock:
                blockLines.append(line)
            
        self.all_dicts=[]
        for block in axesBlocks:
            tmp_dict={}
            for each_line in block:
                # print("LINE %s" % each_line)
                if each_line.startswith("#"):
                    continue
                cols = each_line.split(":")
                if cols[1]=="\n":
                    # print("Column is none")
                    continue
                if len(cols) > 1:
                    key = cols[0]
                    svalue = cols[1]
                    # print(svalue.isdigit())
                    #print(key,svalue)
                    """
                    if self.is_integer(svalue):
                        print("Integer dayo")
                    else:
                        print("Integer dehanaiyo")
                    """
                    tmp_dict[key] = svalue
            # if 'tmp_dict' has values
            if tmp_dict:
                self.all_dicts.append(tmp_dict)
        
        #for ddd in self.all_dicts:
            #print(ddd)

        self.isPrepDict = True

        return self.all_dicts

    # 格納した辞書のリストから指定した軸名のパラメータ辞書をもらう
    def getDictOf(self, axis_name):
        print(f"axis_name:{axis_name}")
        if self.isPrepDict==False:
            self.storeAxesBlocks()

        if self.debug:
            print(self.all_dicts)
            # Display all the dictionaries
            for ddd in self.all_dicts:
                print(ddd['_axis_name'])
        
        for ddiicc in self.all_dicts:
            if self.debug:
                print(ddiicc['_axis_name'],axis_name)
            if ddiicc['_axis_name'] == axis_name:
                # print("FOUND!")
                return ddiicc

    def getHomeValue(self, axis_name):
        if self.isPrepDict==False:
            self.storeAxesBlocks()
        dddd = self.getDictOf(axis_name)
        if '_val2pulse' in dddd.keys():
            homevalue = float(dddd['_home_value'])
            return homevalue

    # 軸名を指定してパルス分解能など動かすときに必要な情報を得る
    def getPulseInfo(self, axis_name):
        dddd = self.getDictOf(axis_name)
        val2pulse = 9999999.999999
        sense = 1
        isGotPulseResol = False
        isGotSense = False
        isGotHomeValue = False
        # pulse resolution
        if '_val2pulse' in dddd.keys():
            val2pulse = float(dddd['_val2pulse'])
            isGotPulseResol = True
        if '_sense' in dddd.keys():
            sense = int(dddd['_sense'])
            isGotSense = True

        if '_home_value' in dddd.keys():
            homevalue = float(dddd['_home_value'])
            isGotHomeValue = True
        
        if isGotPulseResol and isGotSense and isGotHomeValue:
            return val2pulse, sense, homevalue
        else:
            print("Fatal errors.")
            sys.exit()

    def getLimit(self, axis_name):
        dddd = self.getDictOf(axis_name)
        # lower limit flag
        lower_limit = 0.0
        upper_limit = 99999.99999

        if '_lower_limit' in dddd.keys():
            lower_limit = float(dddd['_lower_limit'])
        else:
            print("No lower limit")
            sys.exit()

        if '_upper_limit' in dddd.keys():
            upper_limit = float(dddd['_upper_limit'])
        else:
            print("No lower limit")
            sys.exit()

        return lower_limit, upper_limit
    
    def makeListOnOff(self):
        if self.isRead == False:
            self.storeLine()

        # 最初にOn Offポジションが設定してある行をすべてDictに格納する
        initial_dicts = []
        
        for line in self.lines:
            line = line.strip()
            if line.startswith("#") :
                continue
            if "On_Position" in line:
                tmp_str=line.replace("_On_Position","")
                axis_name, param= (tmp_str.split(":"))
                # param に "#" ｂが含まれて場合はそれ以降はコメントとして扱う   
                if param.rfind("#") != -1:
                    param = param[:param.rfind("#") - 1]
                tmp_dic = {"axis_name":axis_name, "param":param, "on-off":"on"}
                initial_dicts.append(tmp_dic)
                continue
            if "Off_Position" in line:
                tmp_str=line.replace("_Off_Position","")
                axis_name, param= (tmp_str.split(":"))
                # param に "#" ｂが含まれて場合はそれ以降はコメントとして扱う   
                if param.rfind("#") != -1:
                    param = param[:param.rfind("#") - 1]
                tmp_dic = {"axis_name":axis_name, "param":param, "on-off":"off"}
                initial_dicts.append(tmp_dic)
                continue

        matched_list=[]
        self.on_off_list=[]

        # 軸の名称で整理する
        for idx1,data1 in enumerate(initial_dicts):
            if data1['axis_name'] in matched_list:
                # print("Already okay!")
                continue
            for idx2,data2 in enumerate(initial_dicts[idx1+1:]):
                # print("Comparing", data1,data2)
                if data1['axis_name'] == data2['axis_name']:
                    matched_list.append(data1['axis_name'])
                    #print(data1['param'], data2['param'])
                    for d in [data1, data2]:
                        if d['on-off'] == 'on':
                            onpos = float(d['param'])
                        if d['on-off'] == 'off':
                            offpos = float(d['param'])
                    # print(onpos,offpos)
                    tmpdic = {
                        "axis_name":data1['axis_name'],
                        "on": onpos,
                        "off": offpos
                    }
                    self.on_off_list.append(tmpdic)
                    break

        # ここまでの作業で以下のような辞書ができる　2022/03/24　10:39
        # [{'on': 70.0, 'axis_name': 'Light_1', 'off': -50.0}, {'on': 80.0, 'axis_name': 'Ssd_1', 'off': -9.0}, {'on': -18.974, 'axis_name': 'Beam_Stop_1', 'off': 24.375}, {'on': 22.447, 'axis_name': 'Collimator_1', 'off': 9.3}, {'on': 58.0, 'axis_name': 'Beam_Monitor', 'off': -39.0}, {'on': 43.0, 'axis_name': 'Intensity_Monitor', 'off': -39.0}, {'on': 5.2, 'axis_name': 'Cryostream_1', 'off': 14.8}]
        return self.on_off_list

    # 退避軸の定義は非常に難しい@bss.config
    # ここでは type_axis というのを指定して bss.config を読んで
    # 0. _axis_commentに "evacuate"　& 'type_axis' が含まれている軸を探し
    # (この時点でY軸なのかZ軸なのかってのが決まる)
    # 1. val2pulse, sense　を取得する
    # 2. それとは別に On position / Off positionの情報を読む
    # 3. On position / Off position は軸の名前で定義されている
    #    type_axis で指定したやつの mm 単位でのOn/Off位置をゲットする
    # 4. 最終的にその軸の変換係数をかけて pulse の On/Off を返す
    def getEvacuateInfo(self, type_axis, the_2nd = False):
        if self.isPrepDict == False:
            self.storeAxesBlocks()

        nth_axis = 0
        for dict in self.all_dicts:
            if self.debug:
                print("!!!!!!!!!!!!!!!!!!!!!!!!!1")
                print(dict)
                print("!!!!!!!!!!!!!!!!!!!!!!!!!1")
            if "_axis_comment" in dict:
                axis_comment = dict['_axis_comment']
                if type_axis in axis_comment:
                    if axis_comment.rfind("evacuate") != -1:
                        if self.debug:
                            print("Found evacuate axis")
                            print(type_axis, dict['_axis_name'])
                            print("Found evacuate axis")
                        evac_axis = dict['_axis_name']
                        val2pulse, sense, home_value = self.getPulseInfo(dict['_axis_name'])
                        if the_2nd == False:
                            break
                        elif the_2nd == True and nth_axis==0:
                            nth_axis+=1
                            continue
                        else:
                            break

        self.makeListOnOff()

        for on_off_line in self.on_off_list:
            axis_string=on_off_line['axis_name'].lower().replace("_"," ")
            if self.debug:
                print("axis_string=",axis_string)
            if axis_string.rfind(type_axis)!=-1:
                on_mm = float(on_off_line['on'])
                off_mm = float(on_off_line['off'])
                # Include home value to estimate the pulse position On/Off
                on_pulse = int(val2pulse * (on_mm * sense + home_value))
                off_pulse = int(val2pulse * (off_mm * sense + home_value))
                return evac_axis, on_pulse, off_pulse

    # Lightだけはなぜか特別 (2025/03/07) -> 退避軸としては設定されていないので要注意
    def getLightEvacuateInfo(self, axis_name):
        light_dic = self.getDictOf(axis_name)
        on_off_list = self.makeListOnOff()
        val2pulse, sense, homevalue = self.getPulseInfo(axis_name)

        if self.debug:
            print(on_off_list)

        for on_off_line in on_off_list:
            tmp_axis_name = on_off_line['axis_name']
            axis_name = tmp_axis_name.lower().split("_")[0]
            if axis_name == "light":
                # Unit [mm]
                on_pos = float(on_off_line['on'])
                off_pos = float(on_off_line['off'])
                # Unit [pulse]
                self.on_pulse = int(on_pos*val2pulse*sense)
                self.off_pulse = int(off_pos*val2pulse*sense)
                self.isPrep = True
                print("Light position: ON/OFF %s/%s"% (self.on_pulse, self.off_pulse))
                return self.on_pulse, self.off_pulse

    def getEvacInfo(self, axis_name):
        target_dic = self.getDictOf(axis_name)
        on_off_list = self.makeListOnOff()
        val2pulse, sense, homevalue = self.getPulseInfo(axis_name)

        for on_off_line in on_off_list:
            tmp_axis_name = on_off_line['axis_name']
            axis_name = tmp_axis_name.lower().split("_")[0]
            if axis_name == "intensity":
                # Unit [mm]
                on_pos = float(on_off_line['on'])
                off_pos = float(on_off_line['off'])
                # Unit [pulse]
                self.on_pulse = int(on_pos*val2pulse*sense)
                self.off_pulse = int(off_pos*val2pulse*sense)
                self.isPrep = True
                print("Intensity monitor position: ON/OFF %s/%s"% (self.on_pulse, self.off_pulse))
                return self.on_pulse, self.off_pulse

    def get(self, confstr):
        if self.isRead == False:
            self.storeLines()

        isFound = False
        for line in self.lines:
            # skip "#" character
            if line[0] == "#":
                continue
            if line.find(confstr) != -1:
                isFound = True
                fstr = line
                break

        # check if the string was found
        if isFound == False:
            raise MyException("config string was not found:%s"%confstr)

        # strip after "#"
        if fstr.rfind("#") != -1:
            print(fstr)
            fstr = fstr[:fstr.rfind("#") - 1]

        # ":" treatment
        return fstr[fstr.rfind(":") + 1:]

    def getValue(self, confstr):
        strvalue = self.get(confstr)
        # print strvalue
        return float(strvalue)

    def getCmount(self):
        try:
            self.mx = self.getValue("Cmount_Gonio_X_Magnet")
        except:
            self.mx = self.getValue("Cmount_Gonio_X")
        try:
            self.mz = self.getValue("Cmount_Gonio_Z_Magnet")
        except:
            self.mz = self.getValue("Cmount_Gonio_Z")
        self.my = self.getValue("Cmount_Gonio_Y_Magnet")
        return self.mx, self.my, self.mz

    def getCryo(self):
        if self.isPrep == False:
            self.readEvacuate()
        return self.cryo_on, self.cryo_off

    def getBS(self):
        if self.isPrep == False:
            self.readEvacuate()
        return self.bs_on, self.bs_off

    def getColli(self):
        if self.isPrep == False:
            self.readEvacuate()
        return self.colli_on, self.colli_off

    def getThinnestAtt(self):
        if self.isRead==False:
            self.storeLines()
        # list of thickness
        thick_list=[]

        min_thick = -9999

        for line in self.lines:
            if line.rfind("Seamless_Min_Thickness:") != -1:
                cols=line.split()
                min_thick=float(cols[1])
        if min_thick < 0.0:
            min_thick = 0.0

        return min_thick

    def getThinnestAtt_ORIGINAL(self):
        if self.isRead==False:
            self.storeLines()
        # list of thickness
        thick_list=[]

        for line in self.lines:
            if line.startswith("#")==True:
                continue
            if line.rfind("Attenuator1_") != -1:
                cols=line.split()
                if len(cols) == 4:
                    thickness = float(cols[2].replace("um",""))
                    thick_list.append((cols[0], thickness))
                else:
                    print("skipping this line %s" % line)

        sorted_thick = sorted(thick_list, key=lambda x:x[1])
        min_thick = sorted_thick[1][1]

        return min_thick


# def getCLinfo(self):
# try:
# self.cl_hv=self.getValue("_home_value")
# self.cl_sense=self.getValue("_sense")
# self.cl_val2pulse=self.getValue("_home_value")
#
# except MyException,ttt:
# print ttt.args[0]

if __name__ == "__main__":
    bssconf = BSSconfig()

    # Cmount position
    x,y,z=bssconf.getCmount()
    print(f"{x:.5f} {y:.5f} {z:.5f}")
    #bssconf.getThinnestAtt()

    """
    # axis_name="st1_col_1_z"
    # print(bssconf.getPulseInfo(axis_name))
    #e,a,b=bssconf.getEvacuateInfo("collimator")
    # beamline.ini を読む
    from configparser import ConfigParser, ExtendedInterpolation
    config = ConfigParser(interpolation=ExtendedInterpolation())
    config.read("%s/beamline.ini" % os.environ['ZOOCONFIGPATH'])
    # 'bs_evacinfo'
    info = config.get("axes", "bs_evacinfo")
    
    #e,a,b=bssconf.getEvacuateInfo(info)
    #print(e,a,b)

    #print(bssconf.readZoomOption())
    #axis_name = "st2_coax_1_x"

    #bssconf.getSense(axis_name)

    # collimator evacuation parameters
    print("#####################3")
    e,a,b=bssconf.getEvacuateInfo("collimator")

    # Beam stopper evacuation parameters
    print("#####################3")
    e,a,b=bssconf.getEvacuateInfo("beam stop")
    print(e,a,b)

    print("#####################3")
    e,a,b=bssconf.getEvacuateInfo("cryo")

    print(bssconf.getDictOf("st2_detector_1_x"))

    print(e,a,b)

    print("################################")
    print(bssconf.getLimit("st2_detector_1_x"))
    print(bssconf.getHomeValue("st2_detector_1_x"))

    """