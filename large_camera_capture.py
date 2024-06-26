import socket,os,sys,datetime,time
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")

host="192.168.163.12"
port=920920

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print "OKAY"

starttime=datetime.datetime.now()
client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client.connect((host,port))

pinimg="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/large.jpg"

client.send("from nadechin")
response=client.recv(4096)
dt=datetime.datetime.now()


tstr=datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

prefix="%s"%tstr
mv_command="mv %s %s.jpg"%(pinimg,prefix)
os.system(mv_command)

endtime=datetime.datetime.now()

print starttime
print endtime
