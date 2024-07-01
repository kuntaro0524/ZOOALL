#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys,os
import smtplib
import datetime
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
from email.MIMEMultipart import MIMEMultipart
from email.Header import Header
from email.Utils import formatdate

def create_message(from_addr, to_addr, subject, body, encoding):
    msg = MIMEMultipart()
    msg['Subject'] = Header(subject, encoding)
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Date'] = formatdate()

    related = MIMEMultipart('related')
    alt = MIMEMultipart('alternative')
    related.attach(alt)

    print body
    content = MIMEText(body, 'plain', encoding)
    alt.attach(content)

    return msg
    pass

def create_message_text(self, to_addr, subject, body, encoding):
    msg = MIMEText(body)
    msg['Subject'] = Header(subject, encoding)
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Date'] = formatdate()

    return msg
    pass


def send_via_gmail(from_addr, to_addr, msg):
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login('bl32xu@gmail.com', 'microfocus')
    s.sendmail(from_addr, [to_addr], msg.as_string())
    s.close()

if __name__ == '__main__':
    from_addr = 'bl32xu@gmail.com'
    to_addr = 'kunio.hirata@riken.jp; naoki.sakai@riken.jp'
    #to_addr = 'narita.hirotaka@gmail.com; kunio.hirata@riken.jp'
    title = "Message from ZOO"
    date="%s"%(datetime.datetime.now())
    body = "%s\n"%date

###################
    sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs")
    import Date
    import sqlite3,time,numpy
    import ESA

    time_date = Date.Date()

    while(1):
        esa = ESA.ESA(sys.argv[1])
        conds_dict = esa.getDict()

        logline=""
        lap_array = []
        n_collected = 0
        n_notcollect = 0
        for cond in conds_dict:
            if cond['isDS']!=0:
                n_collected += 1
                logline+="PUCK:%s"%cond['puckid']
                logline+="-%02d"%cond['pinid']
                logline+=" %s"%cond['sample_name']
                if cond['mode']=="helical":
                    logline+=" NHE=%s "%cond['nds_helical']
                elif cond['mode']=="multi":
                    logline+=" NDS=%s "%cond['nds_multi']

                starttime = "%s"%cond['t_meas_start']
                endtime   = "%s"%cond['t_ds_end']
                t1 = time_date.getTimeFromZooDB(starttime)
                t2 = time_date.getTimeFromZooDB(endtime)
                lap = time_date.getDiffMin(t1,t2)
                logline+="%s Lap=%5.1f min. \n"%(t1,lap)
                lap_array.append(lap)

                #print starttime
                #tmpstr="%d"%starttime
                #print tmpstr[0:4]
                #print tmpstr[4:7]
                #print tmpstr[8:10]
                #st=datetime.datetime.strptime(starttime,'%Y-%m-%d %H:%M:%S')
                #logline+=" Start    %s"%starttime
                #logline+=" Finished %s\n"%endtime
            else:
                n_notcollect += 1
                continue
        
        mean_lap_time = numpy.array(lap_array).mean()
        
        logline+="Collected from %3d pins. %3d pins remained.\n"%(n_collected, n_notcollect)
        exp_min = n_notcollect * mean_lap_time
        exp_hour = exp_min / 60.0
        logline+="Mean time/pin = %5.1f min.\n"%mean_lap_time
        logline+="Expected remained time: %5.1f mins. (%5.1f hours)\n"%(exp_min,exp_hour)
        nowtime = datetime.datetime.now()
        exp_finish_time = nowtime + datetime.timedelta(hours = exp_hour)
        logline+="Expected finishing time: %s\n"%(exp_finish_time)
        print logline

        msg = create_message_text(from_addr, to_addr, title, logline, 'utf-8')
        send_via_gmail(from_addr, to_addr, msg)
        print "Now sleeping for 15mins...."
        time.sleep(60*15)
