import os,sys, subprocess

command = "git status"
output = subprocess.check_output(command, shell=True)

# column 1: ID, 5: run status

lines = output.split("\n")
icount = 0
readFlag=False

for line in lines:
    if line.rfind("Untracked files:") != -1:
        readFlag = True
        continue
    if readFlag:
        if line.startswith("#"):
            #print(line)
            cols=line.split()
            if len(cols) == 2:
                filename=line.split()[1]
                if filename.endswith(".py"):
                    print(filename)
    else:
        continue
