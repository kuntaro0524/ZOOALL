import os, sys, glob

title = "TEST"
picpath = "./CPS1573-01/raster.jpg"

def getHTMLstring(title, picpath):
    each_html = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title> test </title>
</head>
<body>
        <p> %s  </p>
        <img src="%s" alt="%s" title="Raster results">
</body>
</html>
    """ % (title, picpath, title)

    return each_html

piclist = glob.glob("./CPS*.png")

print piclist

for pic in piclist:
    print getHTMLstring(pic, pic)
