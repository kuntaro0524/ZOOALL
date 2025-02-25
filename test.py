import os,sys

file_path=sys.argv[1]
file_paths_list = []

for filepath in open(file_path).readlines():
    file_paths_list.append(filepath.strip())

copy_list=[]
for file_path in file_paths_list:
    print(file_path)
    # cut down '/' 
    cols = file_path.split('/')
    len_cols = len(cols)

    if (cols[1]=="zoo45xu") and cols[2]=="Libs":
        copy_list.append(f"cp -Rf {file_path} ./Libs/")
    elif (cols[1]=="zoo45xu" and len_cols==3):
        copy_list.append(f"cp -Rf {file_path} ./")
    else:
        copy_list.append(f"cp -Rf {file_path} ./HOGE/{cols[2]}/")


# copy scripts
ofile=open("copy.sh","w")
for copy_str in copy_list:
    ofile.write(copy_str+"\n")
ofile.close()
    