from django.db import models


class Publication(models.Model):
    """
    A data publication posted to our api which contains Measurements for
    MeasurementSites.
    """

    type = models.CharField(
        max_length=255,
        help_text=(
            "The type of publication. One of: TrafficFlow, TravelTime, "
            "IndividualTravelTime"
        ),
    )
    reference_id = models.CharField(
        max_length=255,
        help_text=(
            "Unique publication identifier. The ID is a unique for data set delivered "
            "by the system and shall remain unchanged throughout the system lifetime"
        ),
    )
    version = models.CharField(
        max_length=255,
        help_text=(
            "The version of the publication. Incremented (+1) every time section "
            "and/or route definition are modified i.e., a) New section(s) and/or "
            "trajectory(ies) are activated, b) Existing section(s) and/or "
            "trajectory(ies) are deactivated c)	Existing section(s) and/or "
            "trajectories are modified"
        ),
    )
    publication_time = models.DateTimeField(
        help_text=(
            "The date time the latest version (refer attribute 'version') "
            "for this publication was published in UTC format: ISO 8601 "
            "[https://en.wikipedia.org/wiki/ISO_8601]"
        )
    )

    # The following defines the period against which the statistics were reported.
    # The period is defined either using the measurementStartTime-duration pair
    # or measurementStartTime-measurementendTime pair.
    # A default measurement period of 60s is assumed, if duration and
    # measurementEndTime elements are not present.
    measurement_start_time = models.DateTimeField(
        help_text=(
            "The time recorded here is the starting time of the supply period "
            "in UTC format: ISO 8601 [https://en.wikipedia.org/wiki/ISO_8601]"
        )
    )
    measurement_end_time = models.DateTimeField(
        null=True,
        help_text=(
            "The time recorded here is the ending time of the supply period "
            "in UTC format: ISO 8601 [https://en.wikipedia.org/wiki/ISO_8601]"
        ),
    )


class Measurement(models.Model):
    """
    A measurement for a specific MeasurementSite, published in a Publication.

    NOTE: this model should be removed after the dedeuplication migration.
    """

    publication = models.ForeignKey('Publication', on_delete=models.CASCADE)
    reference_id = models.CharField(max_length=255)  # e.g. "SEC_0001"
    version = models.CharField(max_length=255)  # e.g. "1.0"
    name = models.CharField(max_length=255, null=True)
    type = models.CharField(max_length=255)  # e.g. "section"
    length = models.IntegerField(null=True)


class Measurement2(models.Model):
    """
    A measurement for a specific MeasurementSite, published in a Publication.

    NOTE: this model should be renamed to Measurement after the dedeuplication migration.
    """

    publication = models.ForeignKey('Publication', on_delete=models.CASCADE)
    measurement_site = models.ForeignKey('MeasurementSite', on_delete=models.CASCADE)


class MeasurementSite(models.Model):
    """
    A measurement site that consists of one or more MeasurementLocations.
    """

    reference_id = models.CharField(
        max_length=255,
        help_text=(
            "The measurementsitereference element describes the measurement site "
            "(section or trajectory) against which the values are reported"
        ),
    )
    version = models.CharField(max_length=255)
    name = models.CharField(
        max_length=255,
        null=True,
        help_text=("An optional readable name for the measurement site."),
    )
    type = models.CharField(
        max_length=255,
        help_text=(
            """
        Measurement site type. A measurement site can be either a location, a section
        or a trajectory.
        - Location
        A location refers to a point location in the road network from which data
        (vehicle passages) are collected.  A location consists of one or more
        camera-lane pairs. The Amsterdam Travel time system delivers vehicle count
        per location per lane per vehicle category under the trafficflow publication.
        - Section
        A section refers to a traversible route between two locations.
        The Amsterdam Travel time system delivers the following for the sections
        defined in the system:
        a. Raw, representative and processed travel time values under the traveltime
           publication.
        b. Individual travel time values under the individualtraveltime publication
        - Trajectory
        A trajectory refers to a traversible route created using one or more sections.
        The Amsterdam Travel time system delivers the following for the trajectories
        defined in the system:
        a. Processed, predicted and actual under the traveltime publication.
        """
        ),
    )
    length = models.IntegerField(
        null=True,
        help_text=(
            "This element contains information about the length (in meters) of the "
            "measurement site. Applicable only for sections and trajectories"
        ),
    )
    measurement_site_json = models.JSONField(
        null=False,
        unique=True,
        help_text=(
            "This field is made to include a nested json object containing the measurement"
            " site meta data and locations, its lanes and its respective cameras. If"
            " something changes in the measurement site or any of the locations, lanes or"
            " cameras, new records need to be created for all of them. To be able to test"
            " this somewhat easily, we create a json object in this field to be able to test"
            " for changes in any of those objects by doing a select on all fields of the"
            " measurement site, including this locations_json. Note that the order of keys"
            " in the json objects does not matter when using a native jsonb field."
        ),
    )

    @classmethod
    def get_or_create(cls, measurement_site_json: dict) -> 'MeasurementSite':

        measurement_locations = measurement_site_json.pop('measurement_locations')
        measurement_site, created = MeasurementSite.objects.get_or_create(
            measurement_site_json=measurement_site_json,
            defaults=measurement_site_json,
        )

        # If we created a new measurement site, then the underlying entities
        # (locations, lanes and cameras) also need to be created.
        for measurement_location_json in measurement_locations:

            lanes = measurement_location_json.pop('lanes')
            measurement_location, _ = MeasurementLocation2.objects.get_or_create(
                measurement_site=measurement_site,
                **measurement_location_json,
            )

            for lane_json in lanes:

                cameras = lane_json.pop('cameras')
                lane, _ = Lane2.objects.get_or_create(
                    measurement_location=measurement_location,
                    **lane_json,
                )

                for camera_json in cameras:
                    Camera.objects.get_or_create(
                        lane=lane,
                        **camera_json,
                    )

        return measurement_site


class MeasurementLocation(models.Model):
    """
    A location that is part of the MeasurementSite.
    At most one location exists if the measurement site is of type 'location.
    A maximum of two locations should be present if the measurement site is of type
    'section' (start and end location).
    The number of locations is unbounded if the measurement site is of type
    'trajectory' (start location, end location and all via locations)
    """

    measurement = models.ForeignKey('Measurement', on_delete=models.CASCADE)

    index = models.IntegerField(
        null=True,
        help_text=(
            "The index attribute indicates the order of measurement location in the "
            "measurement site. Optional, if the measurement site is of type 'location'"
        ),
    )


class Lane(models.Model):
    """
    A road lane at a MeasurementLocation.
    """

    measurement_location = models.ForeignKey(
        'MeasurementLocation', on_delete=models.CASCADE
    )
    specific_lane = models.CharField(
        max_length=255,
        help_text=(
            "Indicative name for the lane (lane1, lane2, lane3 … lane9 etc) "
            "used in the Amsterdam Travel Time system. The actual lane number is "
            "available at Camera.lane_number with respect to the camera view direction "
            "at the measurement location."
        ),
    )
    camera_id = models.CharField(max_length=255)  # Are either UUIDs OR ints in strings
    latitude = models.DecimalField(max_digits=9, decimal_places=6)  # Decimal(9,6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)  # Decimal(9,6)
    lane_number = models.IntegerField()  # e.g. 1, 2, 3, 4
    status = models.CharField(max_length=255)  # e.g. "on"
    view_direction = models.IntegerField()  # e.g. 225


class MeasurementLocation2(models.Model):
    """
    A location that is part of the MeasurementSite.
    At most one location exists if the measurement site is of type 'location.
    A maximum of two locations should be present if the measurement site is of type
    'section' (start and end location).
    The number of locations is unbounded if the measurement site is of type
    'trajectory' (start location, end location and all via locations)
    """

    measurement_site = models.ForeignKey('MeasurementSite', on_delete=models.CASCADE)

    index = models.IntegerField(
        null=True,
        help_text=(
            "The index attribute indicates the order of measurement location in the "
            "measurement site. Optional, if the measurement site is of type 'location'"
        ),
    )


class Lane2(models.Model):
    """
    A road lane at a MeasurementLocation.
    """

    measurement_location = models.ForeignKey(
        'MeasurementLocation2', on_delete=models.CASCADE
    )
    specific_lane = models.CharField(
        max_length=255,
        help_text=(
            "Indicative name for the lane (lane1, lane2, lane3 … lane9 etc) "
            "used in the Amsterdam Travel Time system. The actual lane number is "
            "available at Camera.lane_number with respect to the camera view direction "
            "at the measurement location."
        ),
    )


class Camera(models.Model):
    """
    A single camera at a measurement location.
    """

    reference_id = models.CharField(
        max_length=255,
        help_text=(
            "The unique camera identifier (defined by the ANPR data supplier). "
            "Format: UUIDv4"
        ),
    )
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    lane = models.ForeignKey('Lane2', on_delete=models.CASCADE)
    lane_number = models.IntegerField(
        help_text=(
            "Lanenumber, calculated from the 'middle' of the road. "
            "Lane direction is indicated by being "
            "- positive (regular traffic should be moving away from the camera), or "
            "- negative (regular traffic should be moving towards the camera). "
            " For example: "
            "- Left lane with regular traffic moving away from the camera is number: 1 "
            "- Left lane with regular traffic moving towards the camera is number: -1"
            "Rechts v/d middenberg positief (verkeer dat van je af gaat)"
            "Links negatief (verkeer dat naar je toe komt)"
        )
    )
    status = models.CharField(
        max_length=255,
        null=True,
        help_text=(
            "On, off or outage. "
            "On: camera is active for travel-time system and functioning, "
            "Off: camera is not active for travel-time system, "
            "Outage: camera is active for travel-time system, but malfunctioning"
        ),
    )
    view_direction = models.IntegerField(
        help_text=(
            "The direction the camera is looking in, expressed in degrees. "
            "0 and every 22,5 degrees are valid values. "
            "0 equals looking North,  180 degrees equals to South, "
            "90 degrees to East, 270 degrees to West."
        )
    )


class TravelTime(models.Model):
    """
    A Measurement measured over multiple MeasurementLocations which contains
    the general travel time and traffic speed for traffic passing these locations.
    """

    measurement = models.ForeignKey('Measurement', on_delete=models.CASCADE)
    type = models.CharField(
        max_length=255,
        help_text=("One of: raw, representative, processed, predicted, actual"),
    )
    data_quality = models.FloatField(
        null=True, help_text=("Quality of the computed travel time/speed (0...100%)")
    )
    estimation_type = models.CharField(
        max_length=255,
        null=True,
        help_text=(
            "The type of estimation used, one of best, estimated, instantaneous, "
            "reconstituted"
        ),
    )
    travel_time = models.IntegerField(
        help_text=("The computed travel time in seconds.")
    )
    traffic_speed = models.IntegerField(
        help_text=("The computed driving speed in kmph.")
    )


class IndividualTravelTime(models.Model):
    """
    A Measurement measured over multiple MeasurementLocations which contains
    the specific travel time and traffic stpeed for a single vehicle.
    """

    measurement = models.ForeignKey('Measurement', on_delete=models.CASCADE)
    license_plate = models.CharField(max_length=255)
    vehicle_category = models.CharField(max_length=255)
    detection_start_time = models.DateTimeField(
        help_text=(
            "The date time the vehicle was detected at the start location of the "
            "measurement site (section) in UTC format."
        ),
        null=True,
        blank=True,
    )
    detection_end_time = models.DateTimeField(
        help_text=(
            "The date time the vehicle was detected at the end lcoation of the "
            "measurement site (section) in UTC format."
        ),
        null=True,
        blank=True,
    )
    travel_time = models.IntegerField(
        help_text=("The computed travel time in seconds.")
    )
    traffic_speed = models.IntegerField(
        help_text=("The computed driving speed in kmph.")
    )


class TrafficFlow(models.Model):
    """
    TrafficFlow describes the intensity data computed for a specific lane
    in the measurement location.
    """

    measurement = models.ForeignKey('Measurement', on_delete=models.CASCADE)
    specific_lane = models.CharField(
        max_length=255,
        help_text=(
            "Indicative name for the lane (lane1, lane2, lane3 … lane9 etc) used in "
            "the Amsterdam Travel Time system. See Lane.specific_lane."
        ),
    )
    vehicle_flow = models.IntegerField(
        help_text=(
            "Provides the total number of vehicle detections at the "
            "measurement site (location) for the measurement period."
        )
    )


class TrafficFlowCategoryCount(models.Model):
    traffic_flow = models.ForeignKey('TrafficFlow', on_delete=models.CASCADE)
    count = models.IntegerField()
    type = models.CharField(max_length=255, null=True)
