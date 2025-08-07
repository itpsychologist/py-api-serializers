from rest_framework import serializers
from cinema.models import (
    CinemaHall,
    Actor,
    MovieSession,
    Genre,
    Movie,
    Order,
    Ticket)


class CinemaHallSerializer(serializers.ModelSerializer):
    class Meta:
        model = CinemaHall
        fields = ("id", "name", "rows", "seats_in_row", "capacity")


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = "__all__"


class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = ("id", "first_name", "last_name", "full_name")


class MovieSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)
    actors = ActorSerializer(many=True, read_only=True)

    class Meta:
        model = Movie
        fields = ("id", "title", "description", "duration", "genres", "actors")


class MovieListSerializer(MovieSerializer):
    genres = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="name"
    )
    actors = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="full_name"
    )

    class Meta:
        model = Movie
        fields = ("id", "title", "description", "duration", "genres", "actors")


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = "__all__"


class MovieSessionSerializer(serializers.ModelSerializer):
    movie = MovieListSerializer(read_only=True)
    cinema_hall = CinemaHallSerializer(read_only=True)

    # For write operations, accept IDs
    movie_id = serializers.IntegerField(write_only=True)
    cinema_hall_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = MovieSession
        fields = ("id", "show_time", "movie", "cinema_hall")

    def create(self, validated_data):
        # Extract the IDs and create the instance
        movie_id = validated_data.pop("movie_id")
        cinema_hall_id = validated_data.pop("cinema_hall_id")

        movie_session = MovieSession.objects.create(
            movie_id=movie_id,
            cinema_hall_id=cinema_hall_id,
            **validated_data
        )
        return movie_session

    def update(self, instance, validated_data):
        # Handle updates with IDs if provided
        if "movie_id" in validated_data:
            instance.movie_id = validated_data.pop("movie_id")
        if "cinema_hall_id" in validated_data:
            instance.cinema_hall_id = validated_data.pop("cinema_hall_id")

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class MovieSessionListSerializer(MovieSessionSerializer):
    movie_title = serializers.CharField(source="movie.title", read_only=True)
    cinema_hall_name = serializers.CharField(
        source="cinema_hall.name",
        read_only=True)
    cinema_hall_capacity = serializers.IntegerField(
        source="cinema_hall.capacity",
        read_only=True)

    class Meta:
        model = MovieSession
        fields = (
            "id",
            "show_time",
            "movie_title",
            "cinema_hall_name",
            "cinema_hall_capacity")
