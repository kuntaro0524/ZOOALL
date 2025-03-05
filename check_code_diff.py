import glob,os

local_lib_files = glob.glob("./Libs/*.py")
local_main_files = glob.glob("./*.py")

# BL32XU files
bl32xu_lib_files = glob.glob("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/*.py")
bl32xu_main_files = glob.glob("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/*.py")


# local libs 
for local_lib_file in local_lib_files:
    local_fname = local_lib_file.split('/')[-1]
    
    for bl32xu_lib_file in bl32xu_lib_files:
        target_name = bl32xu_lib_file.split('/')[-1]
        if local_fname == target_name:
            os.system("echo \"##################################### %s\" >> log" % local_lib_file)
            os.system("diff %s %s >> log" % (local_lib_file, bl32xu_lib_file))

# Main libs
for local_main_file in local_main_files:
    local_fname = local_main_file.split('/')[-1]
    
    for bl32xu_main_file in bl32xu_main_files:
        target_name = bl32xu_main_file.split('/')[-1]
        if local_fname == target_name:
            os.system("echo \"##################################### %s\" >> main.diff" % target_name)
            os.system("diff %s %s >> main.diff" % (local_main_file, bl32xu_main_file))
