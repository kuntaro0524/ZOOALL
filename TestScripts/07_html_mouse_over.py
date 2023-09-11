import os, sys, math, datetime, time, glob

time_str =time.strftime("%Y-%m-%d %H:%M:%S")

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
""" % dict(name = "BL32XU Starting up", root_dir ="/isilon/BL32XU/BLsoft/PPPP/10.Zoo", datename = "START", cdate = time_str)

print(html_head)

png_list = glob.glob("*.png")

idx = 0
for pngfile in png_list:
    idx+=1
    abspath = os.path.abspath(pngfile)

    s = """
  <td><a href="%(pngfile)s" onmouseover="document.getElementById('ph-%(idx)d').style.display='block';" onmouseout="document.getElementById('ph-%(idx)d').style.display='none';">%(pngfile)s</a><div style="position:absolute;"><img src="%(pngfile)s" height="240" id="ph-%(idx)d" style="zindex: 100; position: absolute; top: -260px; display:none;" /></div></td><br>
""" % dict(pngfile = abspath, idx = idx)
    print(s)
