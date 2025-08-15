import asyncio
import json
import logging
from pathlib import Path

import websockets
from pandas import Timestamp

from .state import AISDataState, load_vessel_codes
from .vector import Vector

###############################################################################
# Preliminaries
###############################################################################

# Make the bounding box larger than your area of interest
UL_BOUNDING_BOX = 40.8, -74.06
LR_BOUNDING_BOX = 40.7, -73.98
BOUNDING_BOX = [UL_BOUNDING_BOX, LR_BOUNDING_BOX]

BOUNDING_BOX_CENTER = (
    (UL_BOUNDING_BOX[0] + LR_BOUNDING_BOX[0]) / 2,
    (UL_BOUNDING_BOX[1] + LR_BOUNDING_BOX[1]) / 2,
)

# Conversion factors for degrees to meters
# These values depend on the latitude and longitude
LATITUDE_DEGREES_TO_METERS = 111_049
LONGITUDE_DEGREES_TO_METERS = 84_465


def get_coordinates(lat, lon):
    return Vector(
        (lon - BOUNDING_BOX_CENTER[1]) * LONGITUDE_DEGREES_TO_METERS,
        (lat - BOUNDING_BOX_CENTER[0]) * LATITUDE_DEGREES_TO_METERS,
    )


###############################################################################
# Utility class for recording data
###############################################################################


class AISStreamDataRecorder:

    def __init__(self, data_dir: Path, message_type: str):
        self.f = open(data_dir / f"{message_type}.json", "a")

    def record(self, message: dict):
        self.f.write(json.dumps(message) + "\n")
        self.f.flush()


###############################################################################
# Main class for connecting to the AIS stream and recording data
###############################################################################


class AISStream:

    def __init__(self, api_key, vessel_codes_file, data_dir: Path):
        self.api_key = api_key
        self.data_dir = data_dir

        logging.log(logging.INFO, f"Recording raw AIS data to {data_dir}")

        self.recorders = dict()
        load_vessel_codes(vessel_codes_file)

        self.ais_data_state = AISDataState()
        self.ais_data_state.start()

        self.keep_running = True

    def run(self):
        while self.keep_running:
            try:
                asyncio.run(self.record_ais_stream())
            except websockets.exceptions.ConnectionClosedError:
                logging.log(logging.CRITICAL, "Connection closed. Reconnecting...")
            except Exception as e:
                logging.exception(f"Exception {e} thrown. Continuing...")
        else:
            logging.log(logging.CRITICAL, "Stopping AIS stream, shutting down...")
            for recorder in self.recorders.values():
                recorder.f.close()
            self.ais_data_state.keep_running = False

    async def record_ais_stream(self):
        async with websockets.connect(
            "wss://stream.aisstream.io/v0/stream"
        ) as websocket:
            subscribe_message = {
                "APIKey": self.api_key,
                # filter by bounding box
                "BoundingBoxes": [BOUNDING_BOX],
                # filter by message types
                "FilterMessageTypes": [
                    "PositionReport",
                    "StandardClassBPositionReport",
                    "ShipStaticData",
                    "StaticDataReport",
                ],
            }

            subscribe_message_json = json.dumps(subscribe_message)
            await websocket.send(subscribe_message_json)

            async for message_json in websocket:
                try:
                    if not self.keep_running:
                        break

                    # parse the incoming message
                    message = json.loads(message_json)
                    message_type = message["MessageType"]
                    metadata = message["MetaData"]
                    message_contents = message["Message"]
                    message_timestamp = (
                        Timestamp(metadata.get("time_utc")[:-10]).value / 1e9
                    )

                    # record all messages for logging purposes
                    if message_type not in self.recorders:
                        self.recorders[message_type] = AISStreamDataRecorder(
                            self.data_dir, message_type
                        )

                    recorder = self.recorders[message_type]
                    recorder.record(message)

                    # process the message
                    if message_type in ["ShipStaticData", "StaticDataReport"]:
                        self.ais_data_state.report_static_data(
                            message_timestamp, message_contents[message_type]
                        )

                    elif message_type in [
                        "PositionReport",
                        "StandardClassBPositionReport",
                    ]:
                        coordinates = get_coordinates(
                            message_contents[message_type]["Latitude"],
                            message_contents[message_type]["Longitude"],
                        )

                        self.ais_data_state.report_position_data(
                            message_timestamp,
                            coordinates,
                            message_contents[message_type],
                        )
                except Exception as e:
                    logging.exception(f"Exception {e} thrown on message {message_json}")
                    logging.log(logging.CRITICAL, "continuing execution...")
                    logging.exception(f"Exception {e} thrown on message {message_json}")
                    logging.log(logging.CRITICAL, "continuing execution...")
