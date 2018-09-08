#!/usr/bin/env python
'''
**********************************************************************
* Filename    : line_with_obsavoidance.py
* Description : An example for sensor car kit to followe line
* Author      : Dream
* Brand       : SunFounder
* E-mail      : service@sunfounder.com
* Website     : www.sunfounder.com
* Update      : Dream    2016-10-08    New release
**********************************************************************
'''

from SunFounder_Line_Follower import Line_Follower
from SunFounder_Ultrasonic_Avoidance import Ultrasonic_Avoidance
from picar import front_wheels
from picar import back_wheels
from picar import ADC
import time
import picar

picar.setup()

# D0~D7 to BCM number
D0 = 17
D1 = 18
D2 = 27
D3 = 22
D4 = 23
D5 = 24
D6 = 25
D7 = 4

ua = Ultrasonic_Avoidance.Ultrasonic_Avoidance(D0)
lf = Line_Follower.Line_Follower()
fw = front_wheels.Front_Wheels(db='config')
bw = back_wheels.Back_Wheels(db='config')
adc = ADC()

lf.read_analog = adc.read


gate_value = 50		# less then the normal, will act
forward_speed = 90
lf_status_last = [0,0,0]

a_step = 20
b_step = 40

FLASH_line_DELAY = 50

REFERENCES = [200, 200, 200, 200, 200]
#calibrate = True
calibrate = False

max_off_track_count = 40
delay = 0.0005

turning_angle = 40
forward_speed = 70
backward_speed = 60

back_distance = 10
turn_distance = 20

def calibration():	# measure 10 times then use the minimal as reference
	print ("calibrating.....")
	references = [0, 0, 0]
	global gate_value

	env0_list = []
	env1_list = []
	env2_list = []
	fw.turn(70)
	bw.forward()
	bw.speed = forward_speed

	for times in xrange(1,10):
		print ("calibrate %d "%times)
		A0 = lf.read_analogs()[0]
		A1 = lf.read_analogs()[1]
		A2 = lf.read_analogs()[2]

		env0_list.append(A0)
		env1_list.append(A1)
		env2_list.append(A2)
		
		time.sleep(0.5)

	references[0] = min(env0_list)
	references[1] = min(env1_list)
	references[2] = min(env2_list)

	for i in xrange(0,3):
		lf.references[i] = references[i] - gate_value

	fw.turn(90)
	bw.stop()
	print ("calibration finished")
	print ("Minimal references =", references)

def state_line():
	#print "start_follow"
	global turning_angle
	off_track_count = 0
	bw.speed = forward_speed

	a_step = 3
	b_step = 10
	c_step = 30
	d_step = 45
	bw.forward()
	while True:
		lt_status_now = lf.read_digital()
		print
		lt_status_now
		# Angle calculate
		if lt_status_now == [1,1,0,1,1]:
			step = 0
		elif lt_status_now == [1,0,0,1,1] or lt_status_now == [1,1,0,0,1]:
			step = a_step
		elif lt_status_now == [1,0,1,1,1] or lt_status_now == [1,1,1,0,1]:
			step = b_step
		elif lt_status_now == [1, 1, 0, 0, 0] or lt_status_now == [0, 0, 0, 1, 1]:
			step = c_step
		elif lt_status_now == [0,1,1,1,1] or lt_status_now == [1,1,1,1,0]:
			step = d_step

		# Direction calculate
		if lt_status_now == [1,1,0,1,1]:
			off_track_count = 0
			fw.turn(90)
		# turn right
		elif lt_status_now in ([1,0,0,1,1], [1,0,1,1,1], [0, 0, 1, 1, 1], [0,1,1,1,1]):
			off_track_count = 0
			turning_angle = int(90 - step)
		# turn left
		elif lt_status_now in ([1,1,0,0,1], [1,1,1,0,1], [1, 1, 1, 0, 0], [1,1,1,1,0]):
			off_track_count = 0
			turning_angle = int(90 + step)
		elif lt_status_now == [1,1,1,1,1]:
			off_track_count += 1
			if off_track_count > max_off_track_count:
				# tmp_angle = -(turning_angle - 90) + 90
				tmp_angle = (turning_angle - 90) / abs(90 - turning_angle)
				tmp_angle *= fw.turning_max
				bw.speed = backward_speed
				bw.backward()
				fw.turn(tmp_angle)

				lf.wait_tile_center()
				bw.stop()

				fw.turn(turning_angle)
				time.sleep(0.2)
				bw.speed = forward_speed
				bw.forward()
				time.sleep(0.2)
		else:
			off_track_count = 0

		fw.turn(turning_angle)
		time.sleep(delay)

def cali():
	references = [1, 1, 1, 1, 1]
	print ("cali for module:\n  first put all sensors on white, then put all sensors on black")
	mount = 100
	fw.turn(70)
	print ("\n cali white")
	time.sleep(4)
	fw.turn(90)
	white_references = lf.get_average(mount)
	fw.turn(95)
	time.sleep(0.5)
	fw.turn(85)
	time.sleep(0.5)
	fw.turn(90)
	time.sleep(1)

	fw.turn(110)
	print ("\n cali black")
	time.sleep(4)
	fw.turn(90)
	black_references = lf.get_average(mount)
	fw.turn(95)
	time.sleep(0.5)
	fw.turn(85)
	time.sleep(0.5)
	fw.turn(90)
	time.sleep(1)

	for i in range(0, 5):
		references[i] = (white_references[i] + black_references[i]) / 2
	lf.references = references
	print ("Middle references =", references)
	time.sleep(1)

def destroy():
	bw.stop()
	fw.turn(90)

def state_sonic():
	#print "start_avoidance"
	distance = ua.get_distance()
	if 0<=distance<back_distance: # backward
		avoid_flag = 2
	elif back_distance<distance<turn_distance : # turn
		avoid_flag = 1
	else:						# forward
		avoid_flag = 0

	print ('distance = ',distance)
	return avoid_flag

def stop():
	bw.stop()
	fw.turn_straight()

def main():
	calibration()
	while True:
		line_flag = state_line()
		avoid_flag = state_sonic()

		# touch obstruction, backward then wait
		if avoid_flag == 2:
			bw.backward()
			bw.speed = backward_speed
			print (" touch obstruction")
			time.sleep(1)
			bw.stop()

		# near obstruction, wait
		elif avoid_flag == 1: 
			print ("  near obstruction")
			time.sleep(1)
			bw.stop()

		# no obstruction, track line
		else:	
			print ("   no obstruction, line_flag = ",line_flag)
			if line_flag == 0:		# direction
				fw.turn(90)
				bw.forward()
				bw.speed = forward_speed
			elif line_flag == 1:	# turn right
				fw.turn(90 - step)
				bw.forward()
				bw.speed = forward_speed
			elif line_flag == 2:	# turn left
				fw.turn(90 + step)
				bw.forward()
				bw.speed = forward_speed
			elif line_flag == 3:	# backward
				fw.turn(90)
				bw.backward()
				bw.speed = forward_speed
			elif line_flag == 4:	# stop to wait line
				fw.turn(90)
				bw.stop()

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		stop()
