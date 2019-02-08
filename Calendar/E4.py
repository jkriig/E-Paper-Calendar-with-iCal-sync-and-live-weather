#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
E-Paper Software (main script) for the 3-colour and 2-Colour E-Paper display
A full and detailed breakdown for this code can be found in the wiki.
If you have any questions, feel free to open an issue at Github.

Copyright by aceisace
"""
from __future__ import print_function
import calendar
from datetime import datetime
from time import sleep
from datetime import timedelta

from settings import *
from icon_positions_locations import *

from PIL import Image, ImageDraw, ImageFont, ImageOps
import pyowm
from ics import Calendar
try:
    from urllib.request import urlopen
except Exception as e:
    print("Something didn't work right, maybe you're offline?"+e.reason)

if display_colours == "bwr":
    import epd7in5b
    epd = epd7in5b.EPD()

if display_colours == "bw":
    import epd7in5
    epd = epd7in5.EPD()

from calibration import calibration

EPD_WIDTH = 640
EPD_HEIGHT = 384
font = ImageFont.truetype(path+'Assistant-Regular.ttf', 18)
im_open = Image.open

"""Main loop starts from here""" 
def main():
    while True:

        time = datetime.now()
        #today = datetime.today()
        hour = int(time.strftime("%-H"))
        month = int(time.now().strftime('%-m'))
        year = int(time.now().strftime('%Y'))

        for i in range(1):
            print('_________Starting new loop___________'+'\n')
            """At the following hours (midnight, midday and 6 pm), perform
               a calibration of the display's colours"""

            if hour is 0 or hour is 12 or hour is 18:
                print('performing calibration for colours now')
                calibration()

            print('Date:', time.strftime('%a %-d %b %y')+', time: '+time.strftime('%H:%M')+'\n')

            """Create a blank white page, for debugging, change mode to
            to 'RGB' and and save the image by uncommenting the image.save
            line at the bottom"""
            image = Image.new('L', (EPD_HEIGHT, EPD_WIDTH), 'white')
            draw = (ImageDraw.Draw(image)).bitmap

            """Draw the icon with the current month's name"""
            #image.paste(im_open(mpath+str(time.strftime("%B")+'.jpeg')), monthplace)
            #image.paste(im_open(mpath+str('oie.jpeg')), monthplace)
           
            """Draw a line seperating the weather and Calendar section"""
            image.paste(seperator, seperatorplace)

            """Draw the icons with the weekday-names (Mon, Tue...) and
               draw a circle  on the current weekday"""
            if (week_starts_on == "Monday"):
                calendar.setfirstweekday(calendar.MONDAY)
                image.paste(weekmon, weekplace)
                draw(weekdaysmon[(time.strftime("%a"))], weekday)

            if (week_starts_on == "Sunday"):
                calendar.setfirstweekday(calendar.SUNDAY)
                draw(weekplace, weeksun)
                image.paste(weeksun, weekplace)
                draw(weekdayssun[(time.strftime("%a"))], weekday)

            """Using the built-in calendar function, draw icons for each
               number of the month (1,2,3,...28,29,30)"""
            cal = calendar.monthcalendar(time.year, time.month)
            #print(cal) #-uncomment for debugging with incorrect dates



            """Custom function to display text on the E-Paper.
            Tuple refers to the x and y coordinates of the E-Paper display,
            with (0, 0) being the top left corner of the display."""
            def write_text(box_width, box_height, text, tuple):
                text_width, text_height = font.getsize(text)
                if (text_width, text_height) > (box_width, box_height):
                    raise ValueError('Sorry, your text is too big for the box')
                else:
                    x = int((box_width / 2) - (text_width / 2))
                    y = int((box_height / 2) - (text_height / 2))
                    space = Image.new('L', (box_width, box_height), color=255)
                    ImageDraw.Draw(space).text((x, y), text, fill=0, font=font)
                    image.paste(space, tuple)

            write_text(350,25, 'OIE Room 308', monthplace)
            """ Handling Openweathermap API"""
            print("Connecting to Openweathermap API servers...")
            owm = pyowm.OWM(api_key)
            if owm.is_API_online() is True:
                observation = owm.weather_at_place(location)
                print("weather data:")
                weather = observation.get_weather()
                weathericon = weather.get_weather_icon_name()
                Humidity = str(weather.get_humidity())
                cloudstatus = str(weather.get_clouds())
                weather_description = (str(weather.get_status()))

                if units == "metric":
                    Temperature = str(int(weather.get_temperature(unit='celsius')['temp']))
                    windspeed = str(int(weather.get_wind()['speed']))
                    write_text(50, 35, Temperature + " °C", (334, 0))
                    write_text(100, 35, windspeed+" km/h", (114, 0))

                if units == "imperial":
                    Temperature = str(int(weather.get_temperature('fahrenheit')['temp']))
                    windspeed = str(int(weather.get_wind()['speed']*0.621))
                    write_text(50, 35, Temperature + " °F", (334, 0))
                    write_text(100, 35, windspeed+" mph", (114, 0))

                if hours == "24":
                    sunrisetime = str(datetime.fromtimestamp(int(weather.get_sunrise_time(timeformat='unix'))).strftime('%-H:%M'))
                    sunsettime = str(datetime.fromtimestamp(int(weather.get_sunset_time(timeformat='unix'))).strftime('%-H:%M'))

                if hours == "12":
                    sunrisetime = str(datetime.fromtimestamp(int(weather.get_sunrise_time(timeformat='unix'))).strftime('%-I:%M'))
                    sunsettime = str(datetime.fromtimestamp(int(weather.get_sunset_time(timeformat='unix'))).strftime('%-I:%M'))

                print('Temperature: '+Temperature+' °C')
                print('Humidity: '+Humidity+'%')
                print('Icon code: '+weathericon)
                print('weather-icon name: '+weathericons[weathericon])
                print('Wind speed: '+windspeed+'km/h')
                print('Sunrise-time: '+sunrisetime)
                print('Sunset time: '+sunsettime)
                print('Cloudiness: ' + cloudstatus+'%')
                print('Weather description: '+weather_description+'\n')

                """Drawing the fetched weather icon"""
                image.paste(im_open(wpath+weathericons[weathericon]+'.jpeg'), wiconplace)

                """Drawing the fetched temperature"""
                image.paste(tempicon, tempplace)

                """Drawing the fetched humidity"""
                image.paste(humicon, humplace)
                write_text(50, 35, Humidity + " %", (334, 35))

                """Drawing the fetched sunrise time"""
                image.paste(sunriseicon, sunriseplace)
                write_text(50, 35, sunrisetime, (249, 0))

                """Drawing the fetched sunset time"""
                image.paste(sunseticon, sunsetplace)
                write_text(50, 35, sunsettime, (249, 35))

                """Drawing the wind icon"""
                image.paste(windicon, windiconspace)

                """Write a short weather description"""
                write_text(144, 35, weather_description, (70, 35))

            else:
                image.paste(no_response, wiconplace)

            """Filter upcoming events from your iCalendar/s"""
            print('Fetching events from your calendar'+'\n')
            print(time.now().strftime('%-m %-d %Y'))
            tomorrow = time.day + 1
            s = str(tomorrow)
            print('Tomorrow : ',tomorrow)
            #print(time.now().strftime('%-m '+ s + ' %Y'))
            
            events_this_month = []
            upcoming = []

            for icalendars in ical_urls:
                ical = Calendar(urlopen(icalendars).read().decode())
                for events in ical.events:
                    #print(events.begin.format('M D YYYY'))
                    allevents = events.begin.format('M D hhA') #+ ' ' events.dtstamp
                    #+ events.name + ' $ ' + 
                    #print('$$$$')
                   # print(allevents)
                    if time.now().strftime('%-m %-d %Y') == (events.begin).format('M D YYYY'):
                        print(events.name)
                        upcoming.append({'date':events.begin.format('MMM D hhmmA'), 'endevent':events.end.format('hhmmA'), 'event':events.name})
                        events_this_month.append(int((events.begin).format('D')))
                    if time.now().strftime('%-m '+ s + ' %Y') == (events.begin).format('M D YYYY'):
                        upcoming.append({'date':events.begin.format('MMM D hhmmA'), 'endevent':events.end.format('hhmmA'), 'event':events.name})
                        events_this_month.append(int((events.begin).format('D')))
                        
                    if month == 12:
                        if (1, year+1) == (1, int((events.begin).year)):
                            upcoming.append({'date':events.begin.format('MMM D hhmmA'),'end':events.end.format('AhhmmA'), 'event':events.name})
                            print('12')
                    if month != 12:
                        if (month+1, year) == (events.begin).format('M YYYY'):
                            upcoming.append({'date':events.begin.format('MMM D hhmmA'),'end':events.end.format('hhmmA'), 'event':events.name})
                            print('else')
               # for timeline in ical.timeline:
               #     print(timeline.now())
                    
                    
            upcoming.reverse()
            print (upcoming)
            print('$$$')
            #del upcoming[7:]
            print ('###')
            print(events_this_month)
            print('$$$')
            print (upcoming)

            def write_text_left(box_width, box_height, text, tuple):
                text_width, text_height = font.getsize(text)
                if (text_width, text_height) > (box_width, box_height):
                    raise ValueError('Sorry, your text is too big for the box')
                else:
                    y = int((box_height / 2) - (text_height / 2))
                    space = Image.new('L', (box_width, box_height), color=255)
                    ImageDraw.Draw(space).text((0, y), text, fill=0, font=font)
                    image.paste(space, tuple)
            #print('$$$')
            """Write event dates and names on the E-Paper"""
            for dates in range(len(upcoming)):
               # write_text(70, 25, (upcoming[dates]['date']), date_positions['d'+str(dates+1)])
                fulldate = upcoming[dates]['date'] + ' to ' +  upcoming[dates]['endevent']
               # print('$_$')
                print(fulldate)
                write_text(250, 25, (fulldate), date_positions['d'+str(dates+1)])

            for events in range(len(upcoming)):
                #write_text_left(314, 25, (upcoming[events]['event']), event_positions['e'+str(events+1)])
                write_text_left(450, 25, (upcoming[events]['event']), event_positions['e'+str(events+1)])
  
            
            print('Date:', time.strftime('%a %-d %b %y')+', time: '+time.strftime('%h:%M')+'\n')
            lastupdate = ('Last Updated at: ' +time.strftime('%H:%M A'))
            write_text(350,25, lastupdate, currenttime)
            #write_text(350,35, 'OIE Room 308', monthplace)
            
            print('Initialising E-Paper Display')
            epd.init()
            sleep(5)
            print('Converting image to data and sending it to the display')
            print('This may take a while...'+'\n')
            epd.display_frame(epd.get_frame_buffer(image.rotate(270, expand=1)))
            # Uncomment following line to save image
            #image.save(path+'test.png')
            del events_this_month[:]
            del upcoming[:]
            print('Data sent successfully')
            print('Powering off the E-Paper until the next loop'+'\n')
            epd.sleep()

            for i in range(1):
                nexthour = ((60 - int(time.strftime("%-M")))*60) - (int(time.strftime("%-S")))
                sleep(nexthour)

if __name__ == '__main__':
    main()
