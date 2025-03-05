import subprocess as sp

output = sp.subprocess.check_output(['git status'],shell=True)

lines = output.split("\n")
icount = 0
for line in lines:
    print(line)
    cols = line.split()
 
    if len(cols) == 9:
        job_id = int(cols[0])
        host_name = cols[7]
        command = "qstat -j %s" % job_id
        output2 = sp.check_output(command, shell = True)

        loglines  = output2.split("\n")

        for logline in loglines:
            if logline.rfind("sge_o_host:") != -1:
                #print logline
                cols = line.split()
            if logline.rfind("stdout_path_list") != -1:
                print host_name,logline.replace("stdout_path_list","").replace("NONE","").replace(":","")
        icount += 1
