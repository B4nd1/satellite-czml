from .czml import (CZML, Billboard, CZMLPacket, Description, Label,
                   Path, Position, Point)

class CZMLManager:
    """
    Generic CZML builder for planes, satellites, or any entity that supports the CZML interface.
    """
    def __init__(self, entities, start_time=None, end_time=None, multiplier=1):
        self.entities = entities
        self.start_time = start_time or min(e.start_time for e in entities)
        self.end_time = end_time or max(e.end_time for e in entities)
        self.multiplier = multiplier

    def get_czml(self):
        interval = f"{self.start_time.isoformat()}/{self.end_time.isoformat()}"
        doc = CZML()
        doc.packets.append(CZMLPacket(
            id='document',
            version='1.0',
            clock={
                "interval": interval,
                "currentTime": self.start_time.isoformat(),
                "multiplier": self.multiplier,
                "range": "LOOP_STOP",
                "step": "SYSTEM_CLOCK_MULTIPLIER"
            }
        ))

        for e in self.entities:
            packet = CZMLPacket(id=e.id)
            packet.availability = interval
            packet.description = Description(e.description)

            if hasattr(e, 'build_marker') and e.build_marker():
                if isinstance(e.build_marker(), Point):
                    packet.point = e.build_marker()
                else:
                    packet.billboard = e.build_marker()

            if hasattr(e, 'build_label'):
                packet.label = e.build_label()
            if hasattr(e, 'build_path'):
                packet.path = e.build_path()
            if hasattr(e, 'build_position'):
                packet.position = e.build_position()

            doc.packets.append(packet)

        return doc.dumps()
