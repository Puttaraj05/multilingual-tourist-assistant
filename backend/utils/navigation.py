def create_navigation_url(
    origin_latitude: float,
    origin_longitude: float,
    destination_latitude: float,
    destination_longitude: float
) -> str:

    return (
        "https://www.google.com/maps/dir/"
        "?api=1"
        f"&origin={origin_latitude},{origin_longitude}"
        f"&destination="
        f"{destination_latitude},{destination_longitude}"
        "&travelmode=driving"
    )