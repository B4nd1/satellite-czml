from .czml import (CZML, Billboard, CZMLPacket, Description, Label,
                   Path, Position, Point)

from datetime import datetime, timedelta, timezone


class Plane:
    """
    CZML representation of an airplane following a list of coordinates.
    coords: list of (lon, lat, alt) triples or (time_offset_seconds, lon, lat, alt)
    """
    def __init__(self, coords, id, name=None, description=None, image=None,
                 color=None, marker_scale=1.5, start_time=None, end_time=None,
                 show_label=True, show_path=True):
        self.id = id
        self.name = name or id
        self.description = description or f"Flight {self.name}"
        self.image = image
        self.color = color or [255, 0, 0, 255]
        self.marker_scale = marker_scale
        self.coords = coords
        self.show_label = show_label
        self.show_path = show_path
        self.start_time = start_time or datetime.now(timezone.utc)
        self.end_time = end_time or (self.start_time + timedelta(hours=1))

        # CZML components
        self.czml_marker = None
        self.czml_label = None
        self.czml_path = None
        self.czml_position = None

    def build_marker(self):
        if self.czml_marker is None:
            if self.image:
                self.czml_marker = Billboard(show=True, image=self.image, scale=self.marker_scale)
            else:
                self.czml_marker = Point(show=True, pixelSize=self.marker_scale*10,
                                         color={"rgba": self.color},
                                         outlineColor={"rgba": [0,0,0,255]},
                                         outlineWidth=2)
        return self.czml_marker

    def build_label(self):
        if self.czml_label is None:
            self.czml_label = Label(text=self.name, show=self.show_label)
            self.czml_label.fillColor = {"rgba": self.color}
            self.czml_label.font = '11pt Lucida Console'
            self.czml_label.outlineColor = {"rgba": [0,0,0,255]}
            self.czml_label.outlineWidth = 2
            self.czml_label.horizontalOrigin = 'LEFT'
            self.czml_label.verticalOrigin = 'CENTER'
            self.czml_label.pixelOffset = {"cartesian2": [12, 0]}
        return self.czml_label

    def build_path(self):
        if self.czml_path is None:
            interval = self.start_time.isoformat() + "/" + self.end_time.isoformat()
            self.czml_path = Path()
            self.czml_path.show = [{"interval": interval, "boolean": self.show_path}]
            self.czml_path.width = 2
            self.czml_path.material = {"solidColor": {"color": {"rgba": self.color}}}

            duration = (self.end_time - self.start_time).total_seconds()
            self.czml_path.leadTime = 0
            self.czml_path.trailTime = duration
            # use cartographic degrees for path positions
            carto = []
            # generate time-tagged positions
            total = len(self.coords)
            # duration = (self.end_time - self.start_time).total_seconds()
            for i, c in enumerate(self.coords):
                if len(c) == 4:
                    t_off, lon, lat, alt = c
                    timestamp = (self.start_time + timedelta(seconds=t_off)).isoformat()
                else:
                    lon, lat, alt = c
                    timestamp = (self.start_time + timedelta(seconds=duration * i/(total-1))).isoformat()
                carto.extend([timestamp, lon, lat, alt])
            self.czml_path.positions = {"cartographicDegrees": carto}
        return self.czml_path

    def build_position(self):
        if self.czml_position is None:
            self.czml_position = Position()
            self.czml_position.referenceFrame = 'FIXED'
            self.czml_position.interpolationAlgorithm = 'LAGRANGE'
            self.czml_position.interpolationDegree = 5
            self.czml_position.epoch = self.start_time.isoformat()
            carto = []
            total = len(self.coords)
            duration = (self.end_time - self.start_time).total_seconds()
            for i, c in enumerate(self.coords):
                if len(c) == 4:
                    t_off, lon, lat, alt = c
                    t = t_off
                else:
                    lon, lat, alt = c
                    t = duration * i/(total-1)
                carto.extend([t, lon, lat, alt])
            self.czml_position.cartographicDegrees = carto
        return self.czml_position

class PlaneCZML:
    """
    Generates a CZML document containing multiple Plane instances.
    """
    def __init__(self, planes, start_time=None, end_time=None, multiplier=1):
        self.planes = planes
        self.start_time = start_time or min(p.start_time for p in planes)
        self.end_time = end_time or max(p.end_time for p in planes)
        self.multiplier = multiplier

    def get_czml(self):
        interval = self.start_time.isoformat() + "/" + self.end_time.isoformat()
        doc = CZML()
        # Document packet
        doc.packets.append(CZMLPacket(id='document', version='1.0',
                                      clock={"interval": interval,
                                             "currentTime": self.start_time.isoformat(),
                                             "multiplier": self.multiplier,
                                             "range": "LOOP_STOP",
                                             "step": "SYSTEM_CLOCK_MULTIPLIER"}))
        # Add planes
        for p in self.planes:
            packet = CZMLPacket(id=p.id)
            packet.availability = interval
            packet.description = Description(p.description)
            if p.image:
                packet.billboard = p.build_marker()
            else:
                packet.point = p.build_marker()
            packet.label = p.build_label()
            packet.path = p.build_path()
            packet.position = p.build_position()
            doc.packets.append(packet)
        return doc.dumps()
