import os,sys
import numpy as np

# Common conditions
common_cond={
'ROOT_DIR':"/isilon/users/target/target/iwata/150724-BL32XU-Auto/",
'DIRE_PREFIX':"test"
}

# PUCK conditions
puck_id="1893"

# Exposure condition
condition_collect_001= {
'BEAM_SIZE':10.0,
'OSC_WIDTH':1.0,
'TOTAL_OSC':5.0,
'EXP_HENDERSON':0.7,
'EXP_TIME':0.15,
'DISTANCE':300.0,
'ATT_RASTER':500.0
}

condition_collect_002= {
'BEAM_SIZE':10.0,
'OSC_WIDTH':1.0,
'TOTAL_OSC':5.0,
'EXP_HENDERSON':0.7,
'EXP_TIME':0.15,
'DISTANCE':300.0,
'ATT_RASTER':500.0
}

# Exposure condition
# (Screening mode)
condition_screen= {
'BEAM_SIZE':10.0,
'OSC_WIDTH':1.0,
'TOTAL_OSC':1.0,
'EXP_HENDERSON':0.7,
'EXP_TIME':1.0,
'DISTANCE':300.0,
'ATT_RASTER':0.0
}

conditions={
'COLLECT_001':condition_collect_001,
'COLLECT_002':condition_collect_002,
'SCREEN_001': condition_screen
}
