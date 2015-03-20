smokeyPi-ab
===========

Now also suitable for a sous vide set up.

A while back I built a homemade smoker based on the designs of Alton Brown:  http://www.foodnetwork.com/videos/channels/altons-pulled-pork.html
<br> It worked and we had some really great eats but it was a lot of work to keep the smoker at the target temperature.  It took constant supervision and tweaking of the heat source to maintain the target temperature. 


To solve that problem (but really mostly to learn something new) I started this personal project.  Using a RasphberryPi to monitor the temperature inside the smoker and controlling the heat source directly will allow me to focus on the food and company instead of the heat source.

The RasphberryPi runs 2 application:
- control.py
  - Record the temperatures received from the probe
  - Sample the temperature readings
  - Decide to turn on or off the heat source to keep the smoker at the target temperature
- web.py - a flask web application
  - Graphs the temperatures in real time  using smoothiecharts
  - Historical Graph using d3js
  - Set the target temperature
  - Enable / disable the heat source

**DO NOT LEAVE ANY SETUP USING THIS CODE UNATTENDED.  I AM NOT RESPONSIBLE FOR ANY DAMAGES**
**Please note** that I am not an expert by any means with electronic circuits **Be careful**

###Project dependencies:

####Hardware:
1. RaspberryPI (any model should work - I used a b+)
2. High Temp Waterproof DS18B20 Digital temperature sensor (http://www.adafruit.com/product/642)
3. Powerswitch tail 2 (http://www.adafruit.com/product/268)

####Software:
1. Flask
2. APScheduler
3. sqlite
4. jquery
5. d3js
6. bootstrap
7. smoothiecharts
8. https://github.com/timofurrer/w1thermsensor

#####Hardware schematic coming soon.
In the meantime you can follow the water proof instructions located here:  https://learn.adafruit.com/adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing/hardware

-
##Screenshots
![Alt text](https://raw.githubusercontent.com/gurumitts/smokeyPi-ab/master/screenshot1.png)
