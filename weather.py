#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
# A script by Dustin Hebecker

'''
INFO:
-For user with conky just run this file. A conky config snipped will be returned (execute in conky with ${execpi TIMEINTERVAL SCRIPTPATH+NAME})
-For user of weather data import this file in your own python code, run init and load variables. The weather conditions can be extracted as member variables of the class weather.
-To log the current weather conditions use the flag -log
'''

import pycurl
from StringIO import StringIO
import json
import argparse
import time
import urllib2
import os.path
import numpy as np


class weather:


	def __init__(self, city=None, tempFile='.weather.tmp', refreshinterval=30, storeIpInfo=False, refresh=False):

		self.wdays=['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
		self.wind_dirs=['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW']
		self.tempFile=tempFile
		if os.path.isfile(tempFile):
			with open(tempFile, 'r') as f:
				self.log=json.load(f)
			self.city=self.log['city']
			self.time=self.log['time']
			self.currentweather=self.log['currentweather']
			self.forecast=self.log['forecast']
		else:
			self.city=None
			self.time=0
			self.currentweather=None
			self.forecast=None
	
		if self.internet_on():
			if not self.refreshCity(city):
				if refresh:
					self.refresh()
				elif (time.time()-self.time)/60.>refreshinterval:
					self.refresh()


	def refresh(self):
		self.apikey='6151f42fb82c1ab87863da29465b594b'
		currentWeatherurl='http://api.openweathermap.org/data/2.5/weather?q='+self.city+'&mode=json&units=metric&appid='+self.apikey		
		forecasturl='http://api.openweathermap.org/data/2.5/forecast/daily?q='+self.city+'&cnt=16&mode=json&units=metric&appid='+self.apikey

		currentweather=json.loads(self.curl(currentWeatherurl))
		forecast=json.loads(self.curl(forecasturl))


		if int(currentweather['cod'])==200 and int(forecast['cod'])==200:
			self.currentweather=currentweather
			self.forecast=forecast
			self.time=time.time()
			self.log={'currentweather':self.currentweather, 'forecast':self.forecast, 'time':self.time, 'city':self.city}
			with open(self.tempFile, 'w') as f:
				json.dump(self.log,f)
		
	def refreshCity(self,city=None):
		if city==None:
			city=self.getCurrentCity()
		if city and city!=self.city:
			self.city=city
			self.refresh()
			return True
		return False

	def getCurrentCity(self):
		ipInfo=self.curl('http://ip-api.com/json')
		ipInfo=json.loads(ipInfo)#sotore in additional file for statistics
		if ipInfo["status"]=="fail":
			return FALSE
		else:
			city=ipInfo['city']+'.'+ipInfo['countryCode']
		return city

	def internet_on(self):
	    try:
	        response=urllib2.urlopen('http://www.google.com',timeout=1)
	        response.close
	        return True
	    except urllib2.URLError as err: 
	    	pass
	    return False

	def curl(self, url):
		buffer = StringIO()
		c = pycurl.Curl()
		c.setopt(c.URL, url)
		c.setopt(c.WRITEDATA, buffer)
		c.perform()
		c.close()
		body = buffer.getvalue()
		buffer.close()
		return body



	def returnData(self, value):
		return 1


	def load_variables(self):
		offset=time.time()-self.time

		aday=24*60*60

		if time.localtime().tm_year==time.localtime(self.time).tm_year:
			if time.localtime().tm_yday==time.localtime(self.time).tm_yday:
				self.doffset=0
			else:
				self.doffset=time.localtime().tm_yday-time.localtime(self.time).tm_yday
		else:
			if time.localtime().tm_year==time.localtime(self.time).tm_year+1:
				self.doffset=time.localtime().tm_yday-time.localtime(self.time).tm_yday+365+[0,1][time.localtime(self.time).tm_year%4==0]
			else:
				self.doffset=1000
		if self.doffset>12:
			return 'N/A'
		
#{"coord":{"lon":13.52,"lat":52.46},"weather":[{"id":501,"main":"Rain","description":"moderate rain","icon":"10d"}],"base":"stations","main":{"temp":279,"pressure":1018,"humidity":100,"temp_min":278.15,"temp_max":279.26},"visibility":5000,"wind":{"speed":4.6,"deg":60},"rain":{"1h":1.02},"clouds":{"all":75},"dt":1444830600,"sys":{"type":1,"id":4878,"message":0.007,"country":"DE","sunrise":1444800586,"sunset":1444839183},"id":2859103,"name":"Oberschoneweide","cod":200}

#{"city":{"id":2643743,"name":"London","coord":{"lon":-0.12574,"lat":51.50853},"country":"GB","population":0},"cod":"200","message":0.0095,"cnt":2,"list":[
#{"dt":1451217600,"temp":{"day":13.25,"min":10.46,"max":13.25,"night":10.46,"eve":12.44,"morn":13.25},"pressure":1026.94,"humidity":94,"weather":[{"id":500,"main":"Rain","description":"light rain","icon":"10d"}],"speed":7.51,"deg":231,"clouds":80,"rain":0.49},
#{"dt":1451304000,"temp":{"day":9.81,"min":7.7,"max":10.26,"night":10.26,"eve":9.5,"morn":7.7},"pressure":1023.01,"humidity":90,"weather":[{"id":801,"main":"Clouds","description":"few clouds","icon":"02d"}],"speed":7.7,"deg":160,"clouds":24}]}

		self.cond_now_description =  self.currentweather["weather"][0]["description"] if self.doffset==0 else self.forecast['list'][self.doffset]["weather"][0]["description"]
		self.cond_tom_description = self.forecast['list'][self.doffset+1]["weather"][0]["description"]
		self.cond_tdat_description = self.forecast['list'][self.doffset+2]["weather"][0]["description"]
		self.cond_tdatdat_description = self.forecast['list'][self.doffset+3]["weather"][0]["description"]
		self.cond_now = self.currentweather["weather"][0]["main"] if self.doffset==0 else self.forecast['list'][self.doffset]["weather"][0]["main"]
		self.cond_tom = self.forecast['list'][self.doffset + 1]["weather"][0]["main"]
		self.cond_tdat = self.forecast['list'][self.doffset + 2]["weather"][0]["main"]
		self.cond_tdatdat = self.forecast['list'][self.doffset + 3]["weather"][0]["main"]

		self.temp_now = self.currentweather["main"]["temp"] if self.doffset==0 and "temp" in self.currentweather["main"].keys() else (self.forecast['list'][self.doffset]["temp"]["min"]+self.forecast['list'][self.doffset]["temp"]["max"])/2.

		self.temp_m_now = self.forecast['list'][self.doffset]["temp"]["max"]
		self.temp_m_tom = self.forecast['list'][self.doffset + 1]["temp"]["max"]
		self.temp_m_tdat = self.forecast['list'][self.doffset + 2]["temp"]["max"]
		self.temp_m_tdatdat = self.forecast['list'][self.doffset + 3]["temp"]["max"]

		self.temp_l_now = self.forecast['list'][self.doffset]["temp"]["min"]
		self.temp_l_tom = self.forecast['list'][self.doffset + 1]["temp"]["min"]
		self.temp_l_tdat = self.forecast['list'][self.doffset + 2]["temp"]["min"]
		self.temp_l_tdatdat = self.forecast['list'][self.doffset + 3]["temp"]["min"]

		self.city_name = self.forecast['city']['name']
		self.last_update = time.ctime(self.time) #self.currentweather["dt"])
		self.humidity = self.currentweather["main"]['humidity'] if self.doffset==0 else self.forecast['list'][self.doffset]['humidity']
		self.wind_speed = self.currentweather['wind']['speed'] if self.doffset==0 else self.forecast['list'][self.doffset]['speed']
		if 'deg' in self.currentweather['wind'].keys() or self.doffset!=0:
			self.wind_dir = self.currentweather['wind']['deg'] if self.doffset==0 else self.forecast['list'][self.doffset]['deg']
		else:
			self.wind_dir = 'N/A'
		self.wind_dira = 'N/A' if self.wind_dir == 'N/A' else self.wind_dirs[int((self.wind_dir+45/4)*16./360.-1)]
		self.pressure = self.currentweather["main"]['pressure'] if self.doffset==0 else self.forecast['list'][self.doffset]['pressure']
		temp_e = 0.348*(self.humidity*0.06105*np.exp(17.27*self.temp_now/(237.7+self.temp_now)))
		self.feels_like = self.temp_now + temp_e - 0.7*self.wind_speed #+ 0.7*1350/(self.wind_speed+10) - 4.25 # radiation is solar constant
		gamma = np.log(self.humidity/100.)+(17.67*self.temp_now)/(243.5+self.temp_now)
		self.dew_point = 243.5*gamma/(17.67-gamma)
		self.amount_of_rain = self.forecast['list'][self.doffset]['rain'] if 'rain' in self.forecast['list'][self.doffset].keys() else self.forecast['list'][self.doffset]['snow'] if 'snow' in self.forecast['list'][self.doffset].keys() else 0
		self.visibility = self.currentweather['visibility'] if 'visibility' in self.currentweather.keys() and self.doffset==0 else 'N/A'
		self.sunrise = str(time.localtime(self.currentweather["sys"]['sunrise']).tm_hour) + ':' + str("%02d" %time.localtime(self.currentweather["sys"]['sunrise']).tm_min)
		self.sunset = str(time.localtime(self.currentweather["sys"]['sunset']).tm_hour) + ':' + str("%02d" %time.localtime(self.currentweather["sys"]['sunset']).tm_min)
		self.cloud_coverage = self.currentweather['clouds']['all'] if self.doffset==0 else self.forecast['list'][self.doffset]['clouds']
		self.wday = time.localtime().tm_wday


	def make_conky_string(self, debug=False):
		# self.cond_to_letter()

		config='${color white}' + '\n'
		config+='${font ConkyWeather:size=50}E${font}${voffset -38}${font Comic Sans MS:size=28}' + str("%.1f" %self.temp_now) + '${voffset -15}${font ConkyWeather:size=70} ' + self.cond_to_letter(self.cond_now_description) + '$font' + '\n'
		config+='${color #f5f5dc}${font Comic Sans MS:size=16}' + self.wdays[(self.wday+1)%7] + ' ${alignc}' + self.wdays[(self.wday+2)%7] + ' ${alignr 40}' + self.wdays[(self.wday+3)%7] + '\n'
		config+='${color white}${font ConkyWeather:size=60}' + self.cond_to_letter(self.cond_tom_description) + '${alignc}${font ConkyWeather:size=60} ' + self.cond_to_letter(self.cond_tdat_description) + '${alignr 20}${font ConkyWeather:size=60}' + self.cond_to_letter(self.cond_tdatdat_description) + '$font' + '\n'
		config+='${color #f5f5dc}${font DejaVu Sans:size=12}     ' + str("%.f" %self.temp_l_tom) + ' / ' + str("%.f" %self.temp_m_tom) + '${alignc -25}' + str("%.f" %self.temp_l_tdat) + ' / ' + str("%.f" %self.temp_m_tdat) + '   ${alignr 20}' + str("%.f" %self.temp_l_tdatdat) + ' / ' + str("%.f" %self.temp_m_tdatdat) + '    \n'
		config+='${color white}${font DejaVu Sans:size=10}${voffset 4}Location:${color green}${alignr}' + self.city_name + '\n'
		config+='${color white}Last Updated: ${color green}${alignr} ' + str(self.last_update) + '\n'
		config+='${color white}Apparent Temperature:${color green}${alignr}' + str("%.f" %self.feels_like) + ' C\n'
		config+='${color white}Dew Point: ${color green}${alignr}' + str("%.f" %self.dew_point) + ' C\n'
		config+='${color white}Current Condition:${color green}${alignr}' + self.cond_now_description + '\n'
		config+='${color white}Amount of Precip: ${color green}${alignr}' + str(self.amount_of_rain) + ' mm\n'
		config+='${color white}Humidity: ${color green}${alignr}' + str(self.humidity) + ' %\n'
		config+='${color white}Wind: ${color green}${alignr}' + self.wind_dira + ' - ' + str(self.wind_speed) + ' m/s\n'
		config+='${color white}Pressure: ${color green}${alignr}' + str(self.pressure) + ' mbar\n'
		config+='${color white}Visibility: ${color green}${alignr}' + str(self.visibility) + ' m\n'
		config+='${color white}Cloud Coverage: ${color green}${alignr}' + str(self.cloud_coverage) + ' %\n'
		config+='${color white}Sunrise: ${color green}${alignr}' + str(self.sunrise) + '\n'
		config+='${color white}Sunset: ${color green}${alignr}' + str(self.sunset) + '\n'
		if debug:
			config+=self.cond_now + "\n"
			config+=self.cond_tom_description  + "  " + self.cond_tom  + "\n"
			config+=self.cond_tdat_description + "  " + self.cond_tdat  + "\n"
			config+=self.cond_tdatdat_description + "  " + self.cond_tdatdat  + "\n"
		return config


	def make_conky_file(self, file_=".currentweather"):
		with open(file_, 'w') as f:
			f.write(self.make_conky_string())


	def print_conky_string(self, debug=False):
		print self.make_conky_string(debug=debug)


	def make_log_string(self):
		pc_time = time.localtime()
		pc_month = time.strftime("%b");

		time_str = ( str(pc_time.tm_year) + "-" + str(pc_month) + "-" + str(pc_time.tm_mday).zfill(2) + " " + str(pc_time.tm_hour).zfill(2) + ":" + str(pc_time.tm_min).zfill(2) + ":" + str(pc_time.tm_sec).zfill(2) + " " + time.strftime("%Z", time.localtime()) + ["", "+"][-time.timezone/3600 > 0] + str(-time.timezone/3600) )

		weather_str = (  time_str + "   " + str(-0) + " " + str("%.1f" %self.temp_now) + " " + str("%.1f" %self.dew_point) + " " + str(0) + " " + str("%.1f" %self.humidity) + " " + str(self.wind_speed) +
					" " + str(self.wind_dir) + " " + str(self.wind_dira) + " " + str(0) + " " + str("%.1f" %self.feels_like) + " " + str(self.amount_of_rain) +
					" " + str(self.pressure) + "\n")

		return weather_str


	def make_log_file(self, file_=os.path.join(os.path.expanduser('~') , 'internet_weather.txt')):
		if os.path.isfile(file_):
			with open(file_, 'a') as f:
				f.write(self.make_log_string())
		else:
			legend1 = "#date       time               T_i   T_a  Dewp    H_i  H_a     Wspd   Wdir  Wdir   Gust Chill     Rain   Pressure\n"
			legend2 = "#                              °C    °C    °C      %    %      m/s      °          m/s    °C       mm        hPa\n"
			with open(file_, 'w') as f:
				f.write(legend1+legend2)
				f.write(self.make_log_string())


	def print_log_string(self):
		print self.make_log_string()

	#individual extraction (from file)
	def returnGeneral(self):#TODO
		return 3

	def returnRAW(self):
		return self.log


	def cond_to_letter(self, cond):
		if cond=='sky is clear' or cond=='Clear' or cond=='Sky is Clear':
			return 'a'
		elif cond=='Fair':
			return 'b'
		elif cond=='scattered clouds':
			return 'b'
		elif cond=='partly cloudy' or cond=='few clouds':
			return 'c'
		elif cond=='broken clouds':
			return 'd'
		elif cond=='Clouds':
			return 'e'
		elif cond=='mostly cloudy':
			return 'e'
		elif cond=='overcast clouds':
			return 'f'
		elif cond=='chance of rain':
			return 'g'
		elif cond=='light rain showers' or cond=='light intensity drizzle' or cond=='light intensity drizzle rain':
			return 'h'
		elif cond=='Rain' or cond=='rain':
			return 'i'
		elif cond=='warm rain':
			return 'j'
		elif cond=='chance of a thunderstorm':
			return 'k'
		elif cond=='thunderstorm and rain':
			return 'l'
		elif cond=='Thunderstorm':
			return 'm'
		elif cond=='HeavyThunderstormsAndRain':
			return 'n'
		elif cond=='chance of snow':
			return 'o'
		elif cond=='light snow':
			return 'p'
		elif cond=='Snow' or cond=='snow':
			return 'q'
		elif cond=='freezing':
			return 'r'
		elif cond=='light rain':
			return 's'
		elif cond=='moderate rain':
			return 's'
		elif cond=='LightDrizzle':
			return 's'		 
		elif cond=='_':
			return 't'
		elif cond=='_':
			return 'u'
		elif cond=='_':
			return 'v'
		elif cond=='_':
			return 'w'
		elif cond=='_':
			return 'x'
		elif cond=='snow showers' or cond=='light snow showers':
			return 'y'
		elif cond=='_':
			return 'z'		 
		elif cond=='mist':
			return '9'
		elif cond=='ShallowFog':
			return '9'
		elif cond=='Fog' or cond=='fog' or cond=='haze':
			return '9'
		else:
			return '-'



if __name__=='__main__':

	parser = argparse.ArgumentParser(description='A programm to obtain current weather and the forecast for your current location.')#Change of location is easily possible
	parser.add_argument('-r', '--refresh', dest="REFRESH", action='store_true', default=False, help='Force data refresh.')
	parser.add_argument('-rt', '--refreshtime', dest="REFRESHTIME", action='store', type=int, default=30, help='Refresh interval in minutes.')
	parser.add_argument('-t', '--tempfile', dest="TEMPFILE", action='store', type=str, default=os.path.join(os.path.expanduser('~') , '.weather.tmp'), help='Define the path of the temp file for storage.')
	parser.add_argument('-l', '--location', dest="LOCATION", action='store', type=str, default=None, help='Fore a different location "city name(.country code)".')
	parser.add_argument('-d', '--debug', dest="DEBUG", action='store_true', default=False, help='Helps adding additional weather conditions to font/ttf display.')
	parser.add_argument('-f', '--writeToFile', dest="FILE", action='store', type=str, default=None, help='Stores conky config in file instead of promting it on the commandline.')
	parser.add_argument('-log', '--log', dest="LOG", action='store_true', default=False, help='Returns current weather condition in log format.')
	args = parser.parse_args()



	w=weather(city=args.LOCATION, tempFile=args.TEMPFILE, refreshinterval=args.REFRESHTIME, storeIpInfo=True, refresh=args.REFRESH)
	w.load_variables()
	if args.LOG:
		if args.FILE==None:
			w.print_log_string()
		else:
			w.make_log_file(file_=args.FILE)
	else:
		if args.FILE==None:
			w.print_conky_string(debug=args.DEBUG)
		else:
			w.make_conky_file(file_=args.FILE)

