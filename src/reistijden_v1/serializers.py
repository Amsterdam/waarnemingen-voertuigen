from rest_framework import serializers

from reistijden_v1.models import (
    Camera,
    IndividualTravelTime,
    Lane,
    Measurement,
    MeasurementLocation,
    MeasurementSite,
    Publication,
    TrafficFlow,
    TrafficFlowCategoryCount,
    TravelTime,
)


class CameraSerializer(serializers.ModelSerializer):
    longitude = serializers.CharField()
    latitude = serializers.CharField()

    class Meta:
        model = Camera
        exclude = ['lane']


class LaneSerializer(serializers.ModelSerializer):
    cameras = CameraSerializer(many=True)

    class Meta:
        model = Lane
        exclude = ['measurement_location']


class MeasurementLocationSerializer(serializers.ModelSerializer):
    lanes = LaneSerializer(many=True)

    class Meta:
        model = MeasurementLocation
        exclude = ['measurement_site']


class TravelTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelTime
        exclude = ['measurement']


class IndividualTravelTimeSerializer(serializers.ModelSerializer):
    """
    Overwrite the detection_start/end_time to be required in the validator
    """

    detection_start_time = serializers.DateTimeField(required=True)
    detection_end_time = serializers.DateTimeField(required=True)

    class Meta:
        model = IndividualTravelTime
        exclude = ['measurement']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TrafficFlowCategoryCount
        exclude = ['traffic_flow']


class TrafficFlowSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True)

    class Meta:
        model = TrafficFlow
        exclude = ['measurement']


class MeasurementSiteSerializer(serializers.ModelSerializer):
    measurement_locations = MeasurementLocationSerializer(many=True)

    class Meta:
        model = MeasurementSite
        exclude = ['measurement_site_json']


class MeasurementSerializer(serializers.ModelSerializer):
    measurement_site = MeasurementSiteSerializer(required=True)
    travel_times = TravelTimeSerializer(many=True, required=True)
    individual_travel_times = IndividualTravelTimeSerializer(many=True, required=True)
    traffic_flows = TrafficFlowSerializer(many=True, required=True)

    class Meta:
        model = Measurement
        exclude = ['publication']


class PublicationSerializer(serializers.ModelSerializer):
    measurements = MeasurementSerializer(many=True)

    class Meta:
        model = Publication
        fields = "__all__"

    def create(self, validated_data):
        measurements = validated_data.pop('measurements')
        publication = Publication.objects.create(**validated_data)

        for measurement_src in measurements:
            measurement_site_json = measurement_src.pop('measurement_site')
            measurement_site, _ = MeasurementSite.get_or_create(
                measurement_site_json,
                publication.measurement_start_time,
            )

            measurement = Measurement.objects.create(
                publication=publication,
                measurement_site=measurement_site,
            )

            travel_times = measurement_src.pop('travel_times')
            for travel_time_src in travel_times:
                TravelTime.objects.create(measurement=measurement, **travel_time_src)

            individual_travel_times = measurement_src.pop('individual_travel_times')
            for individual_travel_time_src in individual_travel_times:
                IndividualTravelTime.objects.create(
                    measurement=measurement, **individual_travel_time_src
                )

            traffic_flows = measurement_src.pop('traffic_flows')
            for traffic_flow_src in traffic_flows:
                categories = traffic_flow_src.pop('categories')
                traffic_flow = TrafficFlow.objects.create(
                    measurement=measurement, **traffic_flow_src
                )

                for category_src in categories:
                    TrafficFlowCategoryCount.objects.create(
                        traffic_flow=traffic_flow, **category_src
                    )

        return publication
