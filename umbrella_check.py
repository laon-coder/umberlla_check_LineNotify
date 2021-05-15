#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys
import urllib.parse
import urllib.request
import datetime
import os
# import datetime
from datetime import datetime

WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")
LINE_TOKEN = os.environ.get("LINE_NOTIFY_API_KEY")
city_name = "tokyo"
lat = str(35.6895)
lon = str(139.6917)

# weather api
WEATHER_URL_3h = "http://api.openweathermap.org/data/2.5/forecast?q=" + city_name + "&appid=" + WEATHER_API_KEY
WEATHER_URL_DAILY = "http://api.openweathermap.org/data/2.5/onecall?lat=" + lat + "&lon=" + lon + "&exclude=current,minutely,hourly,alerts&appid=" + WEATHER_API_KEY + "&units=metric"

# LINE notify api
LINE_NOTIFY_URL="https://notify-api.line.me/api/notify"

info_3h_list = []
info_3h = []
timestamp_hhmm = []
list_msg_h3 = []
timestamp = []
msgs = []

def get_weather_3h_info():
    try:
        url = WEATHER_URL_3h
        html = urllib.request.urlopen(url)
        html_json = json.loads(html.read().decode("utf-8"))
    except Exception as e:
        print ("Exception Error: ", e)
        sys.exit(1)
    return html_json

def get_weather_daily_info():
    try:
        url_d = WEATHER_URL_DAILY
        html_d = urllib.request.urlopen(url_d)
        weather_json_d = json.loads(html_d.read().decode("utf-8"))
    except Exception as e:
        print ("Exception Error: ", e)
        sys.exit(1)
    return weather_json_d

def set_weather_3h_info(weather_json):
    lat = weather_json["city"]["coord"]["lat"]
    lon = weather_json["city"]["coord"]["lon"]
    city_name = weather_json["city"]["name"]; # 도시명

    # 아침 6시부터 21시까지 3시간단위의 날씨정보
    for i in range(0, 6):
        info_3h.append(weather_json["list"][2 + i]["weather"][0]["icon"])
        timestamp_3h_dt = datetime.strptime(weather_json["list"][2 + i]["dt_txt"],'%Y-%m-%d %H:%M:%S')
        timestamp_today = timestamp_3h_dt.strftime('%Y-%m-%d')
        timestamp_3h = timestamp_3h_dt.strftime('%H:%M')
        timestamp_hhmm.append(timestamp_3h)

    start_weatherforecast(info_3h)

    msg_header = '\n' + timestamp_today + ' ' + city_name + ' 날씨'
    msgs.append(msg_header)

def start_weatherforecast(info_3h):
    for x in range(len(info_3h)):
        weather_3h = 0
        if (info_3h[x] == '01n' or info_3h[x] == '01d'):
            weather_3h = '맑음☀'
        if (info_3h[x] == '02n' or info_3h[x] == '02d'):
            weather_3h = '약간 흐림🌥️'
        if (info_3h[x] == '03n' or info_3h[x] == '03d'):
            weather_3h = '흐림☁️'
        if (info_3h[x] == '04n' or info_3h[x] == '04d'):
            weather_3h = '먹구름☁'
        if (info_3h[x] == '09n' or info_3h[x] == '09d'):
            weather_3h = '소나기🌧'
        if (info_3h[x] == '10n' or info_3h[x] == '10d'):
            weather_3h = '비🌦️'
        if (info_3h[x] == '11n' or info_3h[x] == '11d'):
            weather_3h = '천둥번개⛈️'
        if (info_3h[x] == '13n' or info_3h[x] == '13d'):
            weather_3h = '눈🌨️'
        if (info_3h[x] == '50n' or info_3h[x] == '50d'):
            weather_3h = '안개🌫️'
        info_3h_list.append(weather_3h) 

def text_edit():
    for z in range(len(info_3h_list)):
        msg_3h = '\n' + timestamp_hhmm[0] + ' ' + info_3h_list[0] + '\n' + timestamp_hhmm[1] + ' ' + info_3h_list[1] + '\n'+ timestamp_hhmm[2] + ' ' + info_3h_list[2] + '\n'+ timestamp_hhmm[3] + ' ' + info_3h_list[3] + '\n'+ timestamp_hhmm[4] + ' ' + info_3h_list[4] + '\n' + timestamp_hhmm[5] + ' ' + info_3h_list[5] + '\n'
    msgs.append(msg_3h)

def set_weather_daily_info(weather_json_d):
    tempMax = round(weather_json_d["daily"][0]["temp"]["max"],1) # 최고기온
    tempMin = round(weather_json_d["daily"][0]["temp"]["min"],1) # 최저기온
    clouds = round(weather_json_d["daily"][0]["clouds"]) # 흐림, %
    dailyPop = weather_json_d["daily"][0]["pop"] # 강수확률(0 or 1)
    
    temper = '\n' + '최고기온 : ' + str(tempMax) + '°C' + '\n' + '최저기온 : ' + str(tempMin) + '°C' + '\n' 
    
    if (clouds <= 20):
        umbrella_chk = '\n' + '잠깐, 햇빛이 뜨거워요!☀️' + '\n' + '양산을 챙기세요🌂'
    else :
        if (dailyPop > 0.0 and 'rain' in weather_json_d["daily"][0]):
            rain = weather_json_d["daily"][0]["rain"] # 강수량　
            if (rain > 0.0):
                umbrella_chk = '\n' + '비 예보가 있어요🌦️' + '\n' + '우산을 챙기세요☔' + '\n' + '(예상 강수량 : ' + rain + '㎜)'
        else :
            umbrella_chk = '\n' + '비 예보가 없어요.' 
    
    msg_d = temper + umbrella_chk
    
    msgs.append(msg_d)
  
def final_text():
    final_msgs = '\n'.join(msgs)
    print(final_msgs)
    send_weather_info(final_msgs)

def send_weather_info(final_msgs):
    
    method = "POST"
    headers = {"Authorization": "Bearer %s" % LINE_TOKEN}
    payload = {"message": final_msgs}
    try:
        payload = urllib.parse.urlencode(payload).encode("utf-8")
        req = urllib.request.Request(
        url=LINE_NOTIFY_URL, data=payload, method=method, headers=headers)
        urllib.request.urlopen(req)
    except Exception as e:
        print ("Exception Error: ", e)
        sys.exit(1)

def weatherNotify():
    weather_json = get_weather_3h_info()
    weather_json_d = get_weather_daily_info()
    set_weather_3h_info(weather_json)
    set_weather_daily_info(weather_json_d)
    text_edit()
    final_text()
