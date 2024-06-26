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
    to_addr = 'kunio.hirata@riken.jp; naoki.sakai@gmail.com; ynakamu7@gmail.com;'
    #to_addr = 'kunio.hirata@riken.jp'
    #to_addr = 'narita.hirotaka@gmail.com; kunio.hirata@riken.jp'
    title = "Message from ZOO45XU"
    date="%s"%(datetime.datetime.now())
    body = "%s\n"%date

###################
    sys.path.append("/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Libs")
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
        n_mounted = 0
        n_planned = len(conds_dict)
        for cond in conds_dict:
            # For all of mounted loops
            isDone = cond['isDone']
            if isDone != 0:
                n_mounted += 1
                logline+="PUCK:%s"%cond['puckid']
                logline+="-%02d"%cond['pinid']
                logline+=" %s"%cond['sample_name']
        
                if isDone == 1:
                    n_collected += 1
                    if cond['mode']=="helical":
                        logline+=" NHE=%s\n"%cond['nds_helical']
                    elif cond['mode']=="multi":
                        logline+=" NDS=%s\n"%cond['nds_multi']
                else:
                    logline+=" Some error occurred.\n"

        n_remain = n_planned - n_mounted
        logline+="Planned number of pins: %3d Mounted: %3d Remained: %3d\n" % (n_planned, n_mounted, n_remain)

        if n_remain == 0:
            logline+="Finished\n"
            msg = create_message_text(from_addr, to_addr, title, logline, 'utf-8')
            send_via_gmail(from_addr, to_addr, msg)
            break

        msg = create_message_text(from_addr, to_addr, title, logline, 'utf-8')
        send_via_gmail(from_addr, to_addr, msg)
        print "Now sleeping for 15mins...."
        time.sleep(15*60)
