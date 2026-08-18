import os
import osmium

from backend.database.mongodb import recommendations_collection


class RecommendationHandler(osmium.SimpleHandler):

    def __init__(self):
        super().__init__()
        self.inserted = 0
        self.skipped = 0

    def add_place(self, tags, latitude, longitude):

        name = tags.get("name")

        if not name:
            self.skipped += 1
            return

        category = None

        # Restaurants
        if tags.get("amenity") == "restaurant":
            category = "restaurant"

        # Cafes
        elif tags.get("amenity") == "cafe":
            category = "cafe"

        # Hotels
        elif tags.get("tourism") == "hotel":
            category = "hotel"

        # Hostels
        elif tags.get("tourism") == "hostel":
            category = "hostel"

        # Museums
        elif tags.get("tourism") == "museum":
            category = "museum"

        # Tourist attractions
        elif tags.get("tourism") == "attraction":
            category = "tourist_attraction"

        # Galleries
        elif tags.get("tourism") == "gallery":
            category = "gallery"

        # Parks
        elif tags.get("leisure") == "park":
            category = "park"

        # Historic places
        elif tags.get("historic") in [
            "monument",
            "castle",
            "fort",
            "archaeological_site"
        ]:
            category = "historic_site"

        if not category:
            self.skipped += 1
            return

        document = {
            "name": name,
            "category": category,
            "latitude": float(latitude),
            "longitude": float(longitude),

            "rating": None,

            "opening_time": tags.get("opening_hours"),

            "address": tags.get("addr:full"),

            "street": tags.get("addr:street"),

            "city": tags.get("addr:city"),

            "country": tags.get("addr:country"),

            "phone": tags.get("phone"),

            "website": tags.get("website"),

            "source": "OpenStreetMap"
        }

        # Prevent duplicate places
        existing = recommendations_collection.find_one({
            "name": name,
            "latitude": float(latitude),
            "longitude": float(longitude)
        })

        if existing:
            self.skipped += 1
            return

        recommendations_collection.insert_one(document)

        self.inserted += 1

        if self.inserted % 100 == 0:
            print(f"Inserted {self.inserted} places...")


    def node(self, node):

        if not node.location.valid():
            return

        self.add_place(
            node.tags,
            node.location.lat,
            node.location.lon
        )


def import_osm(file_path):

    if not os.path.exists(file_path):

        raise FileNotFoundError(
            f"OSM file not found: {file_path}"
        )

    print("=" * 50)
    print("Starting OpenStreetMap import")
    print("=" * 50)

    print(f"OSM file: {file_path}")

    handler = RecommendationHandler()

    handler.apply_file(
        file_path,
        locations=True
    )

    print("=" * 50)
    print("Import completed")
    print(f"Inserted : {handler.inserted}")
    print(f"Skipped  : {handler.skipped}")
    print("=" * 50)


if __name__ == "__main__":

    # Change this when using another country/region
    osm_file = "osm_data/southern-zone-260815.osm.pbf"

    import_osm(osm_file)