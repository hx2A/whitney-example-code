import logging
import time
from dataclasses import dataclass
from datetime import datetime
from threading import Thread

import numpy as np
from pandas import Timestamp

from .vector import Vector

###############################################################################
# Vessel Code Data
###############################################################################

VESSEL_CODES = dict()


def load_vessel_codes(vessel_codes_file):
    global VESSEL_CODES
    with open(vessel_codes_file, "r") as f:
        VESSEL_CODES = {
            int(code): (group, classification.strip())
            for code, group, classification in (
                line.split("|") for line in f.readlines()[1:] if line[0] != "#"
            )
        }


def get_vessel_group(code):
    return VESSEL_CODES[code][0] if code in VESSEL_CODES else "Unknown"


def get_vessel_classification(code):
    return VESSEL_CODES[code][1] if code in VESSEL_CODES else "Unknown"


###############################################################################
# Data Classes
###############################################################################


@dataclass
class ShipInfo:
    name: str
    user_id: str
    call_sign: str
    destination: str
    eta: dict
    dimension: dict
    vessel_group: str
    vessel_classification: str
    timestamp: datetime

    @classmethod
    def parse_ship_static_data(cls, timestamp, ship_static_data):
        return ShipInfo(
            name=ship_static_data["Name"].strip(),
            user_id=ship_static_data["UserID"],
            call_sign=ship_static_data["CallSign"],
            destination=ship_static_data["Destination"].strip(),
            eta=ship_static_data["Eta"],
            dimension=ship_static_data["Dimension"],
            vessel_group=get_vessel_group(ship_static_data["Type"]),
            vessel_classification=get_vessel_classification(ship_static_data["Type"]),
            timestamp=timestamp,
        )

    @classmethod
    def parse_static_data_report(cls, timestamp, static_data_report):
        report_a = static_data_report.get("ReportA", None)
        report_b = static_data_report.get("ReportB", None)
        if report_a and report_b:
            return ShipInfo(
                name=report_a["Name"].strip(),
                user_id=static_data_report["UserID"],
                call_sign=report_b["CallSign"],
                destination="",
                eta={},
                dimension=report_b["Dimension"],
                vessel_group=get_vessel_group(report_b["ShipType"]),
                vessel_classification=get_vessel_classification(report_b["ShipType"]),
                timestamp=timestamp,
            )
        else:
            return None


@dataclass
class PositionReport:
    user_id: int
    coordinates: Vector
    velocity: Vector
    cog: float
    sog: float
    navigational_status: int
    timestamp: datetime

    @classmethod
    def parse_position_report(cls, timestamp, coordinates, position_report):
        navigational_status = position_report.get("NavigationalStatus", 0)

        if navigational_status in [0, 8, 11, 12, 15]:
            heading = position_report["TrueHeading"]
            if heading == 511:
                heading = position_report["Cog"]
                if heading >= 360:
                    heading = 0

            sog = position_report["Sog"]  # in knots
            if sog >= 102.3:
                sog = 0
        else:
            heading, sog = 0, 0

        velocity = Vector.from_heading(np.radians(heading))
        velocity.set_mag(sog * 0.514444)

        return PositionReport(
            user_id=position_report["UserID"],
            coordinates=coordinates,
            velocity=velocity,
            cog=position_report["Cog"],
            sog=position_report["Sog"],
            navigational_status=navigational_status,
            timestamp=timestamp,
        )

    def current_position(self, t) -> Vector:
        return self.coordinates + self.velocity * (t - self.timestamp)

    def future_position(self, t, offset) -> Vector:
        return self.coordinates + self.velocity * (t - self.timestamp + offset)

    @property
    def moving(self) -> bool:
        return (
            self.navigational_status in [0, 8, 11, 12, 15] and self.velocity.mag >= 0.5
        )


###############################################################################
# AIS Data State
###############################################################################


class AISDataState(Thread):

    def __init__(self):
        super().__init__(daemon=True)
        self.static_data = dict()
        self.position_data = dict()

        self.keep_running = True

    def report_static_data(self, timestamp, ship_static_data):
        user_id = ship_static_data["UserID"]
        # Both MessageID 5 and 24 can contain static data but are structured differently
        if user_id not in self.static_data:
            if ship_static_data["MessageID"] == 5:
                self.static_data[user_id] = ShipInfo.parse_ship_static_data(
                    timestamp, ship_static_data
                )
            elif ship_static_data["MessageID"] == 24:
                ship_info = ShipInfo.parse_static_data_report(
                    timestamp, ship_static_data
                )
                if ship_info:
                    self.static_data[user_id] = ship_info

    def report_position_data(self, timestamp, coordinates, position_report):
        position_data = PositionReport.parse_position_report(
            timestamp, coordinates, position_report
        )
        self.position_data[position_data.user_id] = position_data

        # filter out ship position data with timestamps older than 15 minutes
        for user_id, position_data in list(self.position_data.items()):
            if timestamp - position_data.timestamp > 15 * 60:
                del self.position_data[user_id]

    def run(self):
        logging.log(logging.INFO, "Starting AIS data state thread")
        while self.keep_running:
            self.process_ship_data()
            time.sleep(10)
        logging.log(logging.INFO, "Stopping AIS data state thread")

    def process_ship_data(self):
        now = Timestamp.now("UTC").value / 1e9

        for user_id, position_data in self.position_data.items():
            if position_data.moving:
                # ship is moving, better to ignore stationary ships
                ship_info = self.static_data.get(user_id)

                if not ship_info:
                    logging.log(
                        logging.ERROR,
                        f"Ship not found for user_id: {position_data.user_id}",
                    )
                    continue

                current_position = position_data.current_position(now)

                # Print ship info and current position
                # You'll want to expand this to do something useful with the data
                # Use the current position to see if the ship is within your area of interest
                logging.log(logging.INFO, ship_info)
                logging.log(logging.INFO, current_position)
