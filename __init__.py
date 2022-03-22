from mycroft import MycroftSkill, intent_file_handler


class DoorMotionDetection(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('detection.motion.door.intent')
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

