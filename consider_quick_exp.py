import os,sys,math,numpy

osc_width=0.1
rot_range=180.0
n_frame = rot_range/osc_width
dose=10
exp_time=0.1

osc_width_list=[0.1, 0.5, 1.0]
rot_range_list=[180.0,360.0]
dose=10.0
exp_time_list=[0.02,0.01,0.005]

# maximum frame rate
max_frame_rate = 220
# minimum exposure time
min_exp_time = 1.0/max_frame_rate
print(f"Minimum exposure time: {min_exp_time}")

dose_per_sec = 15.0

for osc_width in osc_width_list:
    for rot_range in rot_range_list:
        for exp_time in exp_time_list:
            if exp_time < min_exp_time:
                print(f" Exposure time {exp_time} is too short for the maximum frame rate {max_frame_rate}")
                continue
            n_frame = rot_range/osc_width
            n_frame = int(n_frame)
            total_exposure = exp_time * n_frame

            # rotation speed
            rot_speed = rot_range / total_exposure  

            print(f" Oscillation width: {osc_width} Rotation range: {rot_range} Exposure time: {exp_time} Total exposure: {total_exposure} Rotation speed: {rot_speed}")