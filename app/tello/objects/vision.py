from .structs import Rect
import cv2

TARGET_COLOR = (52, 58, 219)
FACE_FRAME_COLOR = (87, 200, 255)
THRESHOLD_COLOR = (255, 255, 255)

CASCADE = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

class Vision():

    def __init__(self):
        pass

    @staticmethod
    def draw_identifier(frame, target: Rect, color=THRESHOLD_COLOR, text=None, draw_x=True):
        """
        Draws an identifier rectangle on the provided frame, using the target's dimensions
        frame - frame to update
        target - structs.Rect object containing the dimensions of the object to draw
        color - RGB color to use
        text - if provided, the string value will be printed in the top left corner over the rectangle
        draw_x - if true an + will be drawn in the center of the rect
        """
        if (text != None):
            cv2.putText(frame, 'Target', (target.x, target.y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        cv2.rectangle(frame, (target.x, target.y), (target.w+target.x, target.h+target.y), color, 2)
        if draw_x:
            Vision.draw_target_x(target, frame, color)

    @staticmethod
    def track_faces(frame, max_targets=1):
        """
        identifies all the faces present in the frame using the get_faces() function
        max_targets not 1 will currently track all faces
        max_targets = 1 will track the face object with the largest area in the frame
        
        * a rect is drawn over each detected face object and over the combined face area if multiple 
        faces are tracked and detected
        
        target = rect object containing the dimension of the face(s)        
        """
        faces = Vision.get_faces(frame)
        target = Rect(0, 0, 0, 0)

        if (len(faces) == 0):
            return None

        if (max_targets == 1):
            # identify the closest (largest) face in the list
            for (x, y, w, h) in faces:
                target = Rect(x, y, w, h) if target.get_area() < w*h else target

        if (max_targets != 1):
            for (x, y, w, h) in faces:
                Vision.draw_identifier(frame, Rect( x, y, w, h), color=FACE_FRAME_COLOR, text='Face', draw_x=False)
                target = Rect(x, y, w, h) if target == Rect(0, 0, 0, 0) else target.combine(Rect(x, y, w, h))
        
        Vision.draw_identifier(frame, target, color=TARGET_COLOR, text='Target')
        
        return target

    @staticmethod
    def draw_target_x(target, frame, color, length=10):
        """
        Draws a + in the center of the provided target on the provided frame
        frame - frame to update
        target - structs.Rect object containing the dimensions of the object to draw 
        color - RGB color to use
        length - length of the lines in the - (pixles)
        """
        target_ceter = target.get_center()
        cv2.line(frame, [target_ceter.x-length, target_ceter.y], [target_ceter.x+length, target_ceter.y], color, thickness=2)
        cv2.line(frame, [target_ceter.x, target_ceter.y-length], [target_ceter.x, target_ceter.y+length], color, thickness=2)

    @staticmethod
    def get_faces(frame):
        """
        generates an array of detected faces in the frame using the haarcascades classifier
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = CASCADE.detectMultiScale(gray, 1.2, minNeighbors=10, minSize=[20, 20])
        return faces
