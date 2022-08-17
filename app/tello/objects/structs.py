from abc import get_cache_token
import collections

Point = collections.namedtuple('Point', ['x', 'y'])
RC_Command = collections.namedtuple('RC_Command', ['x', 'y', 'z', 'r'])

Automation_Commands = collections.namedtuple('Automation_Commands', ['NILL', 'FOLLOW_PERSONS', 'FOLLOW_PERSON'])
Automation_Options = Automation_Commands(None, 0, 1)


class Rect():
    """
    2D rect object used for describing components on a cv2 frame
    """

    def __init__(self, x, y, w, h) -> None:
        """
        x - x co-ordinate of the object (top left corner of the object)
        y - y co-ordinate of the object (top left corner of the object)
        w - object width in pixles
        h - object height in pixles
        """
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def __eq__(self, __o: object) -> bool:
        if type(__o) != Rect:
            return False
        return self.x == __o.x and self.y == __o.y and self.w == __o.w and self.h == __o.h
    
    def combine(self, __o: object) -> object:
        """
        Combines the object with another rectangle. The result is a new Rect with the minimal area that overlaps both objects 
        """
        if type(__o) != Rect:
            return None
        x = min(self.x, __o.x)
        y = min(self.y, __o.y)
        w = max(self.x + self.w, __o.x + __o.w) - x
        h = max(self.y + self.h, __o.y + __o.h) - y
        return Rect(x, y, w, h)

    def get_center(self) -> Point:
        """
        Returns a Point object representing the center point of the rectangle 
        """
        return Point(int(self.w/2 + self.x), int(self.h/2 + self.y))

    def get_area(self) -> int:
        """
        Returns the total area spanned by the rectangle
        """
        return self.w * self.h
    
    def distance_from_point(self, point) -> Point:
        """
        Returns the distance in pixles from the center of the object and the provided point. 
        The returned values are represented using the Point object but should only be used for x_delta and y_delta
        """
        center = self.get_center()
        return Point(point.x - center.x, point.y - center.y)