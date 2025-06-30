from .czml import CZMLPacket, Billboard, Label, Point, Position, Description
from datetime import datetime, timedelta, timezone

class GroundStation:
    """
    Represents a stationary ground station in CZML.
    """
    def __init__(self, lon, lat, alt, id, name=None, description=None,
                 image=None, color=None, marker_scale=1.5,
                 start_time=None, end_time=None, show_label=True):
        self.id = id
        self.name = name or id
        self.description = description or f"Ground Station {self.name}"
        self.image = image
        self.color = color or [0, 128, 255, 255]
        self.marker_scale = marker_scale
        self.position = (lon, lat, alt)
        self.show_label = show_label
        self.start_time = start_time or datetime.now(timezone.utc)
        self.end_time = end_time or (self.start_time + timedelta(days=1))

    def build_marker(self):
        if self.image:
            return Billboard(show=True, image=self.image, scale=self.marker_scale)
        else:
            return Point(show=True, pixelSize=self.marker_scale * 10,
                         color={"rgba": self.color},
                         outlineColor={"rgba": [0, 0, 0, 255]},
                         outlineWidth=2)

    def build_label(self):
        label = Label(text=self.name, show=self.show_label)
        label.fillColor = {"rgba": self.color}
        label.font = '11pt Lucida Console'
        label.outlineColor = {"rgba": [0, 0, 0, 255]}
        label.outlineWidth = 2
        label.horizontalOrigin = 'LEFT'
        label.verticalOrigin = 'CENTER'
        label.pixelOffset = {"cartesian2": [12, 0]}
        return label

    def build_position(self):
        pos = Position()
        pos.cartographicDegrees = [self.position[0], self.position[1], self.position[2]]
        return pos
