def main():
    import os
    command="ssh 192.168.163.6 \"ps aux | grep video | grep artray | wc -l\""
    os.system(command)

def exec_cmd(cmd):
    from subprocess import Popen, PIPE
    p = Popen(cmd, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    print(out)
    return [ s for s in out.split('\n') if s ]

if __name__ == '__main__':
    main()
