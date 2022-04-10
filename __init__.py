import time
import datetime
import RPi.GPIO as GPIO

from os.path import dirname, join
from mycroft import MycroftSkill, intent_file_handler
from datetime import datetime, timedelta
from mycroft.messagebus.message import Message
from mycroft.util import play_wav
from mycroft.util.format import (nice_date, nice_duration, nice_time,
                                 date_time_format)
from mycroft.util.time import now_utc, to_local, now_local


REMINDER_PING = join(dirname(__file__), 'twoBeep.wav')
MOTION = 18   # GPIO pins
LED = 25
record_list = []       #record the bell time
Bell_GAP_1 = 15.0  # second
Bell_GAP_2 = 120.0
list_clear = 3600  # list will be clear data more than an hour


class DoorMotionDetection(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    def initialize(self):
        my_setting = self.settings.get('my_setting')
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            GPIO.setup(LED, GPIO.OUT)
            GPIO.setup(MOTION, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # enable the pull-up ( pull_up_down=GPIO.PUD_down)
            GPIO.remove_event_detect(MOTION)
            GPIO.add_event_detect(MOTION, GPIO.RISING,
                                  bouncetime=500)  # increase the bouncetime to avoid the event frequently detection
        except:
            self.log.warning("Can't initialize GPIO - skill will not load")
            self.speak_dialog("error.initialize")  # create the error.initialise.dialog file

        finally:
            self.schedule_repeating_event(self.handle_motion,
                                          None, 0.1, 'check_motion')

    def handle_motion(self, message):
        if GPIO.event_detected(MOTION):
            now = now_local()  # catch the current time in the registered location
            next_bell_gap = now - (record_list[-1] if len(record_list) >= 1 else now)  # calculate the gap
            bell_gap_sec = next_bell_gap.total_seconds() # convert to seconds

            if bell_gap_sec > Bell_GAP_2:
                self.bell_ring(3)
                self.speak_dialog("First.Bell")
                record_list.append(now)  # append the time in the list
                #record_list.append([now, day])  # append the time in the list
                
            if bell_gap_sec < Bell_GAP_1:
                if len(record_list) == 0:
                  record_list.append(now)
                  #record_list.append([now, day])                 
                self.bell_ring(3)
                self.speak_dialog("First.Bell")
                
            if Bell_GAP_1 <= bell_gap_sec <= Bell_GAP_2:
                self.bell_ring(2)
                self.speak_dialog("Next.Bell")
                
            if len(record_list) > 5:  # remove the list if more than 5 record
                record_list.pop(0)

    def bell_ring(self, number):
        for x in range(number):
            play_wav(REMINDER_PING)
        time.sleep(.4)

    @intent_file_handler('detection.motion.door.intent')
    def handle_detection_motion_door(self, message):
        dt = record_list[-1]  # get the last value of list
        s = nice_time(dt)
        if(dt.date()== now_local().date()):
            self.speak_dialog("today")
            self.speak_dialog('detection.motion.door', {"time": s})
        else:
            self.speak_dialog('detection.motion.door', {"time": s})
        

def create_skill():
    return DoorMotionDetection()

