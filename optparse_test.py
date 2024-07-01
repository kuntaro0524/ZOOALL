import optparse

parser = optparse.OptionParser()

parser.add_option("--z1", "--zoofile1", dest="filename1", help="ZOO csv/db File No.1.", metavar="FILE")
parser.add_option("--t1", "--time1", dest="timelimit1", help="data collection time in minuts for file1.", metavar="FILE")
parser.add_option("--z2", "--zoofile2", dest="filename2", help="ZOO csv/db File No.2.", metavar="FILE")
parser.add_option("--t2", "--time2", dest="timelimit2", help="data collection time in minuts for file2.", metavar="FILE")
parser.add_option("--q", "--quiet", action="store_false", dest="verbose", default=True,
                  help="don't print status messages to stdout")

print parser.parse_args()

(options, args) = parser.parse_args()

#print type(options), options, options['filename1']

print "Option=", options

#for op in options:
    #print op

#for option in options:
#    print option
