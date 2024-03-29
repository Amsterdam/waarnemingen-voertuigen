import logging
import os
from datetime import datetime
from distutils.util import strtobool

import humps
import xmltodict

logger = logging.getLogger(__name__)


class ReistijdenParser:
    def __init__(self, xml_str):
        super().__init__()
        self.xml_str = xml_str

    def restructure_data(self):
        data_dict = humps.decamelize(xmltodict.parse(self.xml_str.strip()))
        publication_src = data_dict["amsterdam_travel_times"]["payload_publication"]
        measurements = []
        if "site_measurements" in publication_src:
            if type(publication_src["site_measurements"]) is list:
                measurements = [
                    self.measurement_src_to_dict(d)
                    for d in publication_src["site_measurements"]
                ]
            else:
                measurements = [
                    self.measurement_src_to_dict(publication_src["site_measurements"])
                ]

        return {
            "type": publication_src["@type"],
            "reference_id": publication_src["publication_reference"]["@id"],
            "version": publication_src["publication_reference"]["@version"],
            "publication_time": publication_src["publication_time"],
            "measurement_start_time": publication_src["measurement_period"][
                "measurement_start_time"
            ],
            "measurement_end_time": publication_src["measurement_period"][
                "measurement_end_time"
            ],
            "measurement_duration": publication_src["measurement_period"].get(
                "duration"
            ),
            "measurements": measurements,
        }

    def measurement_src_to_dict(self, src_d):
        site_ref = src_d["measurement_site_reference"]
        measurement_site = {
            "reference_id": site_ref["@id"],
            "version": site_ref["@version"],
            "name": site_ref.get("measurement_site_name"),
            "type": site_ref["measurement_site_type"],
            "length": site_ref.get("length"),
            "measurement_locations": self.get_location_from_site_ref(site_ref),
        }
        measurement_site["measurement_site_json"] = measurement_site

        return {
            "measurement_site": measurement_site,
            "travel_times": self.get_travel_times_from_measurement(src_d),
            "individual_travel_times": self.get_individual_travel_times_from_measurement(
                src_d
            ),
            "traffic_flows": self.get_traffic_flows_from_measurement(src_d),
        }

    def get_location_from_site_ref(self, site_ref):
        if "location" in site_ref:
            return [self.location_src_to_dict(site_ref["location"])]
        elif "location_contained_in_itinerary" in site_ref:
            return [
                self.location_src_to_dict(d)
                for d in site_ref["location_contained_in_itinerary"]["location"]
            ]
        return []

    def store_error_content(self, e, request):
        """
        In order to keep the content of the messages that resulted in errors,
        we store them in the container for now. This is a massive hack and should
        be removed very soon. If you find this code, please remove it.
        """
        try:
            error_type = e.__repr__().replace("'", "")
            folder = "/tmp/errors/"
            file_path = f"{folder}{datetime.now().isoformat()}-{error_type}.xml"
            if not os.path.exists(folder):
                os.makedirs(folder)
            with open(file_path, "w") as f:
                f.write(request.body.decode("utf-8"))
        except Exception as e:
            logger.error(e)

    def lane_src_to_dict(self, src_d):
        if type(src_d["camera"]) is list:
            cameras = [self.camera_src_to_dict(camera) for camera in src_d["camera"]]
        else:
            cameras = [self.camera_src_to_dict(src_d["camera"])]

        return {"specific_lane": src_d["@specific_lane"], "cameras": cameras}

    def camera_src_to_dict(self, src_d):
        camera_src = {
            "reference_id": src_d["@id"],
            "lane_number": src_d["lane_number"],
            "status": src_d.get("status"),
            "view_direction": src_d["view_direction"],
        }

        if "coordinates" in src_d:
            camera_src["latitude"] = src_d["coordinates"]["@latitude"]
            camera_src["longitude"] = src_d["coordinates"]["@longitude"]
        else:
            camera_src["latitude"] = None
            camera_src["longitude"] = None

        return camera_src

    def location_src_to_dict(self, src_d):
        if type(src_d["lane"]) is list:
            lanes = [self.lane_src_to_dict(lane) for lane in src_d["lane"]]
        else:
            lanes = [self.lane_src_to_dict(src_d["lane"])]

        return {"index": src_d.get("@index"), "lanes": lanes}

    def travel_time_src_to_dict(self, src_d):
        if (data_error := src_d.get("data_error")) is not None:
            data_error = bool(strtobool(src_d["data_error"]))

        return {
            "type": src_d["@travel_time_type"],
            "data_quality": src_d.get("@data_quality"),
            "estimation_type": src_d.get("@estimation_type"),
            "travel_time": src_d["travel_time"],
            "traffic_speed": src_d["traffic_speed"],
            "num_input_values_used": src_d.get("@number_of_input_values_used"),
            "data_error": data_error,
        }

    def category_src_to_dict(self, src_d):
        return {
            "count": src_d["@count"],
            "type": src_d["@type"] if src_d["@type"] else None
            # Convert empty strings to Null
        }

    def traffic_flow_src_to_dict(self, src_d):
        categories = []
        if "number_of_input_values_used" in src_d:
            category_src = src_d["number_of_input_values_used"]["category"]
            if type(category_src) is list:
                categories = [
                    self.category_src_to_dict(category) for category in category_src
                ]
            else:
                categories = [self.category_src_to_dict(category_src)]

        return {
            "specific_lane": src_d["@specific_lane"],
            "vehicle_flow": src_d["vehicle_flow"],
            "categories": categories,
        }

    def get_travel_times_from_measurement(self, src_d):
        travel_times = []
        if "travel_time_data" in src_d:
            if type(src_d["travel_time_data"]) is list:
                travel_times = [
                    self.travel_time_src_to_dict(travel_time)
                    for travel_time in src_d["travel_time_data"]
                ]
            else:
                travel_times = [self.travel_time_src_to_dict(src_d["travel_time_data"])]
        return travel_times

    ## In Xml for Individual Travel Time the timestamp label is (Camelized) detetection_start/end_time.
    ## It has been renamed to be more consistent with the timestamp name in publication, used in the model.
    ## This was decided together with end-user Leon Deckers
    def get_individual_travel_times_from_measurement(self, src_d):
        individual_travel_times = src_d.get("individual_travel_time_data", [])
        if not (isinstance(individual_travel_times, list)):
            individual_travel_times = [individual_travel_times]

        for individual_travel_time in individual_travel_times:
            self.convert_detection_key(individual_travel_time)

        return individual_travel_times

    def convert_detection_key(self, value):
        """
        Convert the names from the detection start/end times to the correct key values
        detection_start_time -> start_detection_time
        detection_end_time -> end_detection_time
        """
        value['detection_start_time'] = value.pop('start_detection_time', None)
        value['detection_end_time'] = value.pop('end_detection_time', None)

        return value

    def get_traffic_flows_from_measurement(self, src_d):
        traffic_flows = []
        if "traffic_flow_data" in src_d:
            if "measured_flow" in src_d["traffic_flow_data"]:
                traffic_flows_src = src_d["traffic_flow_data"]["measured_flow"]
                if type(traffic_flows_src) is list:
                    traffic_flows = [
                        self.traffic_flow_src_to_dict(measured_flow)
                        for measured_flow in traffic_flows_src
                    ]
                else:
                    traffic_flows = [self.traffic_flow_src_to_dict(traffic_flows_src)]
        return traffic_flows
