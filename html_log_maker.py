import os
import time
import glob
import re

# Reference?: http://demos.jquerymobile.com/1.4.0/popup-iframe/#&ui-state=dialog

class ZooHtmlLog:
    def __init__(self, root_dir, name, online=True):
        self.start_time = time.localtime()
        self.root_dir = root_dir
        self.name = name
        self.online = online

        if self.online:
            self.htmlout = os.path.join(root_dir, time.strftime("report_%y%m%d_%H%M%S.html", self.start_time))
        else:
            self.htmlout = os.path.join(root_dir, "report.html")

        self.make_header()
        self.conditions = []
    # __init__()

    def make_header(self):
        self.html_head = """\
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
""" % dict(name=self.name, root_dir=self.root_dir, datename="started" if self.online else "created",
           cdate=time.strftime("%Y-%m-%d %H:%M:%S", self.start_time))
    # make_header()

    def add_condition(self, condition):
        samples = ["%s (%d pins)" % (x[0], len(x[1])) for x in condition.pucks_and_pins]
        totalpins = sum([len(x[1]) for x in condition.pucks_and_pins])
        info = dict(samples=", ".join(samples),
                    totalpins=totalpins)
        info.update(condition.__dict__)

        s = """
<h3>%(uname)s's sample</h3>
<h4>Conditions</h4>
<table class="dataset_table">
 <tr>
  <th>Beam size [&mu;m]</th> <td>h=%(h_beam).2f, v= %(v_beam).2f</td>
 </tr>
 <tr>
  <th>Raster scan</th> <td>Att= %(att_raster).1f%% trans., Exp= %(raster_exp).3f [s], Loop size= %(loop_size)s</td>
 </tr>
 <tr>
  <th>SHIKA criteria</th> <td>min_score= %(shika_minscore)s, min_dist= %(shika_mindist)s [&mu;m]</td>
 </tr>
 <tr>
  <th>Data collection</th> <td>&Delta;&phi;= %(osc_width).3f&deg;, &phi;-range= %(total_osc).2f&deg;, ExpHenderson= %(exp_henderson).2f [sec], ExpTime= %(exp_time).2f [sec], Distance= %(distance).2f [mm]</td>
 </tr>
 <tr>
  <th>Samples (%(totalpins)d pins)</th> <td>%(samples)s</td>
 </tr>
</table>
""" % info
        self.conditions.append([s])
    # add_condition()
        
    def add_result(self, puckname, pin, h_grid, v_grid, nhits, shika_workdir, prefix, start_time):
        if type(start_time) != str:
            start_time = time.strftime("%Y-%m-%d %H:%M:%S", start_time)

        max_score = read_max_score(os.path.join(shika_workdir, "summary.dat"))
        shika_workdir = os.path.relpath(shika_workdir, self.root_dir)
        phid = "%d-%d" % (len(self.conditions)-1, len(self.conditions[-1])-1)
        s = """
 <tr>
  <td>%(puckname)s</td> <td>%(pin).2d</td> <td>%(h_grid)d&times;%(v_grid)d</td> <td>%(nhits)d</td> <td>%(max_score).1f</td>
  <td><a href="%(shika_workdir)s/loop_before.jpg" onmouseover="document.getElementById('ph-%(phid)s').style.display='block';" onmouseout="document.getElementById('ph-%(phid)s').style.display='none';">loop</a><div style="position:absolute;"><img src="%(shika_workdir)s/loop_before.jpg" height="240" id="ph-%(phid)s" style="zindex: 100; position: absolute; top: -260px; display:none;" /></div>
      <a href="%(shika_workdir)s/%(prefix)s_selected_map.png" onmouseover="document.getElementById('ph2-%(phid)s').style.display='block';" onmouseout="document.getElementById('ph2-%(phid)s').style.display='none';">map</a><div style="position:absolute;"><img src="%(shika_workdir)s/%(prefix)s_selected_map.png" height="600" id="ph2-%(phid)s" style="zindex: 100; position: absolute; top: -620px; display:none;" /></div>
      <a href="%(shika_workdir)s/report_zoo.html">detail</a></td>
  <td>%(start_time)s</td>
 </tr>
""" % locals()
        self.conditions[-1].append(s)
    # add_result()

    def write_html(self):
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

        ofs = open(self.htmlout, "w")
        ofs.write(self.html_head)
        for c in self.conditions:

            for i, r in enumerate(c):
                ofs.write(r)
                if i==0: ofs.write(result_header)

            ofs.write(result_footer)
                
        ofs.write("\n</body>\n</html>\n")
        ofs.close()

# class ZooHtmlLog

re_scanstart = re.compile("Diffraction scan \(([0-9A-Za-z/:\[\] ]+)\)")

def read_diffscanlog(logf):
    h_grid, v_grid, datestr = None, None, None
    for l in open(logf):
        if "Vertical   scan No. of point:" in l:
            v_grid = int(l.split()[5])
        elif "Horizontal scan No. of point:" in l:
            h_grid = int(l.split()[5])
        elif "Diffraction scan " in l:
            r = re_scanstart.search(l)
            datestr = re.sub("\[[A-Za-z]+\] ", "", r.group(1))
            if datestr.count(":") == 3: datestr = datestr[:datestr.rindex(":")]
            datestr = datestr.replace("/","-")

    return h_grid, v_grid, datestr
# read_diffscanlog()

def read_max_score(datf, kind="n_spots"):
    scores = []
    if not os.path.exists(datf): return float("nan")

    for l in open(datf):
        if " %s " % kind in l: scores.append(float(l.split()[4]))

    if len(scores) > 0:
        return max(scores)
    else:
        return float("nan")
# read_max_score()

def read_nhits(wdir):
    found = glob.glob(os.path.join(wdir, "*_selected.dat"))
    assert len(found) <= 1
    if len(found) == 0: return "", 0
    prefix = os.path.basename(found[0]).replace("_selected.dat", "")

    datf = found[0]
    count = 0
    for l in open(datf):
        if l.startswith("#"): continue
        count += 1

    return prefix, count - 1 # first line is header
# read_nhits()

def make_offline(module_name, root_dir, name):
    md = __import__(module_name)
    zhl = ZooHtmlLog(root_dir, name, online=False)

    for cond in md.conditions:
        zhl.add_condition(cond)
        for trayid, pin_list in cond.pucks_and_pins:
            for pinid in pin_list:
                print("doing", trayid, pinid)
                scan_dir = os.path.join(root_dir, "%s-%s-%.2d" % (cond.uname, trayid, pinid), "scan")
                shika_workdir = os.path.join(scan_dir, "_spotfinder")
                raster_log = os.path.join(scan_dir, "diffscan.log")
                if not os.path.exists(raster_log): continue
                h_grid, v_grid, scanstart = read_diffscanlog(raster_log)
                prefix, nhits = read_nhits(shika_workdir)
                zhl.add_result(puckname=trayid, pin=pinid,
                               h_grid=h_grid, v_grid=v_grid,
                               nhits=nhits,
                               shika_workdir=shika_workdir,
                               prefix=prefix,
                               start_time=scanstart)
                zhl.write_html()
# make_offline()

if __name__ == "__main__":
    import sys
    
    root_dir = sys.argv[1]
    name = sys.argv[2]
    module_name = sys.argv[3]

    sys.path.append(os.path.dirname(module_name))
    make_offline(module_name, root_dir, name)
