import sys,os,glob

fdlist=glob.glob("./*")

cwd=os.getcwd()

for fd in fdlist:
    if os.path.isdir(fd)==True:
        cols=fd.split('/')
        if cols[-1].rfind("final")!=-1:
            #print cols[-1]
            final_path=os.path.abspath(fd)



print """
cd %s


"""%(final_path)
