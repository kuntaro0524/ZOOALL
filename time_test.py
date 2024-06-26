import datetime
import time


start_time=datetime.datetime.now()

time_thresh=8.0

while(1):
	current_time=datetime.datetime.now()
	#print start_time
	diff_time=current_time-start_time
	print diff_time.seconds

	if diff_time.seconds > time_thresh:
		print diff_time.seconds
		break
	time.sleep(2.0)
