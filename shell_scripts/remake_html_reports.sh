find -type d -name _spotfinder | xargs -n1 /oys/xtal/cctbx/snapshots/dials-v1-8-3-dev/build/bin/yamtbx.python /oys/xtal/yamtbx.dev/yamtbx/dataproc/myspotfinder/command_line/make_html_report.py mode=zoo # rotate=true

