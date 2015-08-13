#!/usr/bin/python
import sys
import os
import math

def GenerateSeries(gpxFile):
	fp = open(gpxFile, "r")
	latList = []
	lonList = []
	eleList = []
	timeList = []
	PlotFound = False
	Series="{" 
	Series+="     name: '%%_workout_name_%%'," 
	Series+="     data: [" 
	Series+="     	%%_data_%%" 
	Series+="]," 
	Series+="     type: 'spline'," 
	Series+="     tooltip: {" 
	Series+="     	valueDecimals: 2" 
	Series+="     }" 
	Series+="} "
	Data = ""
	SeriesName = ""

	#Load data
	for row in fp:
		row = row.strip()
		if "<name>" in row:
			SeriesName = row.replace("<name>","")
			SeriesName = SeriesName.replace("</name>","")
		if "<trkpt" in row:
			PlotFound = True
			arr = row.split(" ")
			lat = arr[1]
			lon = arr[2]
			lat = lat.replace("lat=","")
			lat = lat.replace('"', "")
			lon = lon.replace("lon=","")
			lon = lon.replace('"',"")
			lon = lon.replace(">","")
			latList.append(float(lat))
			lonList.append(float(lon))

		if not PlotFound: continue
		if "<ele>" in row:
			ele = row.replace("<ele>","")
			ele = ele.replace("</ele>","")
			eleList.append(ele)
		if "<time>" in row:
			arr = row.split("T")
			time = arr[1]
			time = time.replace("Z</time>","")
			timeList.append(time)
	
	SeriesName = gpxFile.split(".gpx")[0].split("/")[1]	
	Series = Series.replace("%%_workout_name_%%",SeriesName)

	TotalSeconds = CalculateSeconds(timeList[0], timeList[len(timeList)-1])
	#print "Total Seconds: ", TotalSeconds 
	Interval = int(TotalSeconds / 300)
	#print "Interval: ", Interval

	#Loop thru data 
	TotalDistance = 0;
	TotalSeconds = 0;
	IntervalSeconds = 0;
	Comma="";
	for i in range(1,len(eleList)):
		#occasionally you get duplicate entries of the same time and location
		if lonList[i-1] == lonList[i] and latList[i-1] == latList[i]: continue
		
		Distance = CalculateDistance(lonList[i-1], latList[i-1], lonList[i], latList[i])
		Seconds = CalculateSeconds(timeList[i-1], timeList[i])
		Speed = CalculateSpeed(Distance, Seconds)
		Elevation = eleList[i]

		TotalDistance += Distance
		TotalSeconds += Seconds
		IntervalSeconds += Seconds
		
		AvgSpeed = CalculateSpeed(TotalDistance, TotalSeconds)

		ChartSpeed = Speed
		ChartSpeed = AvgSpeed
		#output line
		if IntervalSeconds >= Interval or i == len(eleList)-1:
			RoundedDistance = round(TotalDistance, 2)
			RoundedSpeed = round(ChartSpeed, 2)
			#print RoundedDistance, RoundedSpeed
			Data += Comma + "[" + str(RoundedDistance) + ", " + str(RoundedSpeed) + "]" + "\n"
			IntervalSeconds = 0
			Comma = ","

	Series = Series.replace('%%_data_%%',Data)
	return Series 

def CalculateSeconds(t1, t2):
	arr = t1.split(":")
	h1 = arr[0]
	m1 = arr[1]
	s1 = arr[2]
	s1 = s1.split("-")[0]
	
	arr = t2.split(":")
	h2 = arr[0]
	m2 = arr[1]
	s2 = arr[2]
	s2 = s2.split("-")[0]
	if h1 != h2:
		h1 = "1"
		h2 = "2" 	
	Seconds1 = int(s1)*1 + int(m1)*60 + int(h1)*60*60
	Seconds2 = int(s2)*1 + int(m2)*60 + int(h2)*60*60
	return int(Seconds2) - int(Seconds1)

def CalculateDistance(long1, lat1, long2, lat2):
	LongDiff = deg2rad(long1 - long2)
	Lat1 = deg2rad(lat1)
	Lat2 = deg2rad(lat2)
	
	Distance = math.acos(math.sin(Lat1) * math.sin(Lat2) + math.cos(Lat1) * math.cos(Lat2) * math.cos(LongDiff)) * 6371.009
	return Distance 

def CalculateSpeed(d, s):
	return round(d / s * 60 * 60, 2)

def deg2rad(degrees):
	pi = math.pi
	radians = pi * degrees / 180
	return radians

#========================================================================================================
# Processing...
#========================================================================================================
fp = open("MainCompare.html","r")
MainHTML = fp.read()
#print MainHTML

SeriesSection = "series: ["
Comma = ""
for f in sorted(os.listdir("Compare")):
	SeriesSection += Comma + GenerateSeries("Compare/"+f)
	Comma = ","
SeriesSection += "]"

MainHTML = MainHTML.replace("%%_series_%%", SeriesSection)

print MainHTML

