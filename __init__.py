from mycroft import MycroftSkill, intent_file_handler
from mycroft.messagebus.message import Message
#from mycroft.util import play_wav

import time
import RPi.GPIO as GPIO

# REMINDER_PING = join(dirname(__file__), 'twoBeep.wav') # NOT WORKING

# GPIO pins
MOTION = 23
LED = 25
detect_time = []
MOTION_GAP = 60 # second


class DoorMotionDetection(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)
        
    def initialize(self):
        self.register_intent(detection.motion.door, self.handle_detection_motion_door)
        my_setting = self.settings.get('my_setting')
        
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            GPIO.setup(LED, GPIO.OUT)
            GPIO.setup(MOTION, GPIO.IN)  # enable the pull-up ( pull_up_down=GPIO.PUD_down)
            GPIO.add_event_detect(MOTION, self.handle_motion(), GPIO.RISING, bouncetime=500) # increase the bouncetime to avoid the event frequently detection
        except GPIO.error:
            self.log.warning("Can't initialize GPIO - skill will not load")
            self.speak_dialog("error.initialise") # create the error.initialise.dialog file
        finally:
            self.schedule_repeating_event(self.handle_motion(),
                                          None, 0.1, 'motion')
           # my_setting = self.settings.get('my_setting')
            
            
        def handle_motion(self, message):
        if GPIO.event_detected(MOTION):
            now = time.time()           # catch the current time

            """detect_gap is a time gap between the last motion and the current. If it is first then zero.
            Avoiding the first motion to makesure """
            detect_gap = now - detect_time[-1] if len(detect_time) >= 1 else now
            detect_time.append(now)  # append the time in the list

            if detect_gap == MOTION_GAP:
                play_wav(REMINDER_PING)  # play the beep
                self.speak('I still can see the motion at your door')
                detect_time.clear()

            if detect_gap >= 10:
                play_wav(REMINDER_PING)  # play the beep
                self.speak_dialog("DoorDetectionDialog")  # need to create a .dialog file
                self.log.info("GPIO.event_detected")

            self.remove_event_detect(MOTION)    # clear the event
            
            

   # @intent_file_handler('detection.motion.door.intent')
    def handle_detection_motion_door(self, message):
        day = message.data.get('day')
        day_of_time = message.data.get('day_of_time')
        time = ''
        self.speak_dialog('detection.motion.door', data={
            'day': day,
            'day_of_time': day_of_time,
            'time': time
        })


def create_skill():
    return DoorMotionDetection()

