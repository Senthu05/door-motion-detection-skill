from mycroft import MycroftSkill, intent_file_handler
from mycroft.messagebus.message import Message
# from mycroft.util import play_wav

#import time
from datetime import datetime
import RPi.GPIO as GPIO

# REMINDER_PING = join(dirname(__file__), 'twoBeep.wav') # NOT WORKING

# GPIO pins
MOTION = 18
LED = 25
record_list = []
#Bell_GAP = 60  # second
Bell_GAP = 0 days, 0:02:00.00
list_clear = 3600 # list will be clear data more than an hour


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
            #now = time.time()  # catch the current time
            now = datetime.now()
            next_bell_gap = now - record_list[-1] if len(record_list) >= 1 else now

            if next_bell_gap > Bell_GAP:
                self.speak_dialog("First.Bell")
                record_list.append(now)  # append the time in the list

            if next_bell_gap < Bell_GAP:
                self.speak_dialog("Next.Bell")

            for x in record_list:
                if (now - x) > list_clear:
                    record_list.clear()

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
        self.speak_dialog('detection.motion.door', {"time": record_list[-1]})


def create_skill():
    return DoorMotionDetection()

