import sys, datetime
from html_log_maker import ZooHtmlLog
sys.path.append("/isilon/BL45XU/BLsoft/PPPP/10.Zoo/Libs/")

import ESA

dbfile = sys.argv[1]
esa = ESA.ESA(dbfile)
esa.getDict()
conds=esa.getDict()

name = "test"
html_maker = ZooHtmlLog(conds[0]['root_dir'], name, online=False)

def add_result(cond):
    phid = 9999999999
    s = """
 <tr>
  <td>%(puckid)s</td> <td>%(pinid).2d</td> <td>%(n_mount)d&times;%(isSkip)d</td> <td>%(t_mount_end)s</td> <td>%(score_max).1f</td> 
  <td>%(nds_multi)s</td> <td>%(nds_helical)s</td>
    """ % cond

    return s
# add_result()

### HEADER
def make_header(name, root_dir, starttime, online = False):

    html_head = """\
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">

<style>
.dataset_table {
    font-family: "Trebuchet MS", Arial, Helvetica, sans-serif;
    width: 100%%;
    border-collapse: collapse;
}

.dataset_table td, .dataset_table th {
    font-size: 1em;
    border: 1px solid #98bf21;
    padding: 3px 7px 2px 7px;
}

.dataset_table th {
    font-size: 1.1em;
    text-align: left;
    padding-top: 5px;
    padding-bottom: 4px;
    background-color: #A7C942;
    color: #ffffff;
}

.dataset_table tr.alt td {
    color: #000000;
    background-color: #EAF2D3;
}

h1, h2 { text-align: center; text-indent: 0px; font-weight: bold; hyphenate: none;  
      page-break-before: always; page-break-inside: avoid; page-break-after: avoid; }
h3, h4, h5, h6 { text-indent: 0px; font-weight: bold; 
      hyphenate:  none; page-break-inside: avoid; page-break-after: avoid; }

</style>
</head>
<body>
<h1>ZOO report</h1>
<h2>%(name)s</h2>
<div align="right">
root dir: %(root_dir)s<br>
%(datename)s on %(cdate)s
</div>

""" % dict(name=name, root_dir=root_dir, datename="started" if online else "created",
           cdate=starttime)

    return html_head
    # make_header()

loginfo = []

s = """
<h3>%(root_dir)s's sample</h3>
<h4>Conditions</h4>
<table class="dataset_table">
 <tr>
  <th>Beam size [&mu;m]</th> <td>h=%(raster_hbeam).2f, v= %(raster_vbeam).2f</td>
 </tr>
</table>
""" % (conds[0])
loginfo.append([s])

    result_header = """
<h4>Results</h4>
<table class="dataset_table">
 <tr>
  <th rowspan="2">Puck ID</th> <th rowspan="2">Pin</th> <th colspan="4">Raster result</th> <th rowspan="2">Scan started</th>
 </tr>
 <tr>
                <th>Grid</th> <th>Hits</th> <th>MaxScore</th> <th>Detail</th>
 </tr>
"""
    result_footer = "\n</table>\n"

# Header
root_dir = "test/test"
starttime = datetime.datetime.now()
html_head = make_header(name, root_dir, starttime)

for cond in conds:
    if cond['mode'].lower() == "multi":
        nds = cond['nds_multi']
    elif cond['mode'].lower() == "helical":
        nds = cond['nds_helical']
    else:
        nds = 9999

    meas_start = "%s" % cond['t_meas_start']
    Y = meas_start[0:4]
    M = meas_start[4:6]
    d = meas_start[6:8]
    h = meas_start[8:10]
    m = meas_start[10:12]
    meas_start = "%s/%s/%s %02s:%02s" % (Y, M, d, h, m)
    shika_workdir = "%s/%s-%02d/scan00/_spotfinder/" % (cond['root_dir'], cond['puckid'], cond['pinid'])

    #print meas_start
    start_time = datetime.datetime.strptime(meas_start, '%Y/%m/%d %H:%M')


    s = add_result(cond)
    loginfo.append([s])

ofs = open("result.html", "w")
ofs.write(html_head)
for c in loginfo:
    for i, r in enumerate(c):
        ofs.write(r)
        if i==0: ofs.write(result_header)
    ofs.write(result_footer)

ofs.write("\n</body>\n</html>\n")
ofs.close()
