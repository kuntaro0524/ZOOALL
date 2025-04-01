#!/bin/bash
find -type d -name _spotfinder | xargs -n1 /opt/dials/dials-v1-14-13/build/bin2/yamtbx.python /opt/dials/dials-v1-14-13/modules/yamtbx/yamtbx/dataproc/myspotfinder/command_line/make_html_report.py rotate=true
