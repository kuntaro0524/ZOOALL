import optparse, os, sys

parser = optparse.OptionParser()

parser.add_option("--bl", "--beamline", dest="beamline_name", help="The name of your beamline", metavar="FILE")
parser.add_option("--z1", "--zoofile1", dest="filename1", help="ZOO csv/db File No.1.", metavar="FILE")
parser.add_option("--t1", "--time1", dest="timelimit1", help="data collection time in minuts for file1.", metavar="FILE")
parser.add_option("--z2", "--zoofile2", dest="filename2", help="ZOO csv/db File No.2.", metavar="FILE")
parser.add_option("--t2", "--time2", dest="timelimit2", help="data collection time in minuts for file2.", metavar="FILE")
parser.add_option("--z3", "--zoofile3", dest="filename3", help="ZOO csv/db File No.3.", metavar="FILE")
parser.add_option("--t3", "--time3", dest="timelimit3", help="data collection time in minuts for file3.", metavar="FILE")
parser.add_option("--z4", "--zoofile4", dest="filename4", help="ZOO csv/db File No.4.", metavar="FILE")
parser.add_option("--t4", "--time4", dest="timelimit4", help="data collection time in minuts for file4.", metavar="FILE")
parser.add_option("--q", "--quiet", action="store_false", dest="verbose", default=True,
                  help="don't print status messages to stdout")

parser.add_option("--ff", "--from-file", dest="config_file", help="reads a file list", metavar="FILE")

(options, args) = parser.parse_args()

check_list=[options.filename1, options.filename2, options.filename3, options.filename4]
time_list=[options.timelimit1, options.timelimit2, options.timelimit3, options.timelimit4]

# Beamline name
bl_name = options.beamline_name

for zoofile, timelimit in zip(check_list, time_list):
    if (zoofile is None)==False:
        if (timelimit is None)==False:
            pass
        else:
            print("the time limit is set as 99999 minutes because input value is 'None'")
            timelimit=99999

        print((zoofile, timelimit))
