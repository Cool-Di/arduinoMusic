#!/usr/bin/env python

# 8 band Audio equaliser from wav file
 
#import alsaaudio as aa
import pyaudio as aa
from struct import unpack
import numpy as np
import wave
import httplib
import serial
import time

ard = serial.Serial("COM3",57600,timeout=5)
print "Connecting, 5 seconds..."
time.sleep(5) # wait for Arduino

matrix    = [0,0,0,0,0,0,0,0] #fist item - light mode
power     = []
weighting = [2,4,8,16,16,32,64,64] # Change these according to taste

# Set up audio
wavfile = wave.open('music/omen.wav','r')
sample_rate = wavfile.getframerate()
no_channels = wavfile.getnchannels()
chunk       = 4096 # Use a multiple of 8
#output = aa.PCM(aa.PCM_PLAYBACK, aa.PCM_NORMAL)
#output.setchannels(no_channels)
#output.setrate(sample_rate)
#output.setformat(aa.PCM_FORMAT_S16_LE)
#output.setperiodsize(chunk)
p = aa.PyAudio()
output = p.open(format=p.get_format_from_width(wavfile.getsampwidth()), channels=wavfile.getnchannels(), rate=wavfile.getframerate(), output=True)

# Return power array index corresponding to a particular frequency
def piff(val):
	return int(2*chunk*val/sample_rate)
   
def calculate_levels(data, chunk,sample_rate):
	global matrix
	# Convert raw data (ASCII string) to numpy array
	data = unpack("%dh"%(len(data)/2),data)
	data = np.array(data, dtype='h')
	# Apply FFT - real data
	fourier=np.fft.rfft(data)
	# Remove last element in array to make it the same size as chunk
	fourier=np.delete(fourier,len(fourier)-1)
	# Find average 'amplitude' for specific frequency ranges in Hz
	power = np.abs(fourier)   
	#matrix[0]= 1
	matrix[0]= int(np.mean(power[piff(0)    :piff(156):1]))
	matrix[1]= int(np.mean(power[piff(156)  :piff(313):1]))
	matrix[2]= int(np.mean(power[piff(313)  :piff(625):1]))
	matrix[3]= int(np.mean(power[piff(625)  :piff(1250):1]))
	matrix[4]= int(np.mean(power[piff(1250) :piff(2500):1]))
	matrix[5]= int(np.mean(power[piff(2500) :piff(5000):1]))
	matrix[6]= int(np.mean(power[piff(5000) :piff(10000):1]))
	matrix[7]= int(np.mean(power[piff(10000):piff(20000):1]))
	# Tidy up column values for the LED matrix
	matrix=np.divide(np.multiply(matrix,weighting),1000000)
	# Set floor at 0 and ceiling at 9 for LED matrix
	matrix=matrix.clip(0,8)
	return matrix

cmd_off_old = "";

# Process audio file  
timestamp = 0 
print "Processing....."
data = wavfile.readframes(chunk)
while data!='':
	output.write(data)   
	matrix=calculate_levels(data, chunk,sample_rate)
	cmd = "1" #song number
	cmd += "1" #mode number
	cmd_off = ""

	for i in range (0,8):
		cmd = cmd + str(matrix[i])
		
	if ( cmd_off_old == cmd_off and cmd == "" ):
		cmd_off = ""
	#cmd = cmd + "9"
	timestamp = timestamp + 1
	print cmd + "   " + str(timestamp)
	ard.write(str(cmd))
	#msg = ard.read(ard.inWaiting()) # read all characters in buffer
	#print ("Message from arduino: ")
	#print (msg)
	
	data = wavfile.readframes(chunk)

	if ( cmd_off != "" ):
		# conn = httplib.HTTPConnection("192.168.0.14")
		# conn.request("GET", "/sec?cmd=" + cmd_off)
		# conn.close()
		cmd_off_old = cmd_off
