import time
import datetime
import RPi.GPIO as GPIO

from mycroft import MycroftSkill, intent_file_handler
from datetime import datetime, timedelta
from mycroft.messagebus.message import Message
# from mycroft.util import play_wav
from mycroft.util.format import (nice_date, nice_duration, nice_time,
                                 date_time_format)
from mycroft.util.time import now_utc, to_local, now_local

# REMINDER_PING = join(dirname(__file__), 'twoBeep.wav') # NOT WORKING

# GPIO pins
MOTION = 18
LED = 25
record_list = []
Bell_GAP = 15.0  # second
# Bell_GAP = 0:02:00.00
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
            # self.register_intent(detection.motion.door.intent, self.handle_detection_motion_door)


    def handle_motion(self, message):
        if GPIO.event_detected(MOTION):
            now = now_local()  # catch the current time in the registered location 
            #record_list.append(now)
            #next_bell_gap = now - record_list[-1] if len(record_list) >= 1 else now  # calculate the gap   
            if len(record_list) >= 1:
                next_bell_gap = now_local() - record_list[-1]
                self.log.info("I am at if condition")
            else:
                next_bell_gap = now - now
                self.log.info("I am at else condition")
            self.log.info("next_bell_gap = ")
            self.log.info(next_bell_gap)
            bell_gap_sec = next_bell_gap.total_seconds() # convert to seconds
            
           # bell_gap_sec = next_bell_gap / timedelta(seconds=1)  # convert to seconds

            self.log.info("time gap")
            self.log.info(bell_gap_sec)

            if bell_gap_sec < 15 and  bell_gap_sec > 120:
                self.speak_dialog("First.Bell")
                record_list.append(now)  # append the time in the list

            if 15 <= bell_gap_sec <= 120:
                self.speak_dialog("Next.Bell")

            if len(record_list) > 5:  # remove the list if more than 5 record
                record_list.pop(0)

            #             for x in record_list:

    #                 if (now - x) > list_clear:
    #                     record_list.clear()

    @intent_file_handler('detection.motion.door.intent')
    def handle_detection_motion_door(self, message):
        day = message.data.get('day')
        day_of_time = message.data.get('day_of_time')
        time = ''
        #         self.speak_dialog('detection.motion.door', data={
        #             'day': day,
        #             'day_of_time': day_of_time,
        #             'time': time
        #         })
        dt = record_list[-1]  # get the last value of list
        s = nice_time(dt)
#         s = nice_time(dt, self.lang, speech=True,
#                       use_24hour=True, use_ampm=True)  # convet to Pronounce datetime objects
        self.log.info("bell ring time")
        self.log.info(s)
        self.speak_dialog('detection.motion.door', {"time": s})


def create_skill():
    return DoorMotionDetection()

