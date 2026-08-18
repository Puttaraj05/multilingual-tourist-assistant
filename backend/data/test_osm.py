import osmium


class TestHandler(osmium.SimpleHandler):

    def __init__(self):
        super().__init__()
        self.count = 0

    def node(self, node):
        self.count += 1

        if self.count <= 10:
            print(
                self.count,
                node.location.lat,
                node.location.lon,
                node.tags.get("name")
            )


handler = TestHandler()

handler.apply_file(
    "osm_data/southern-zone-260815.osm.pbf",
    locations=True
)

print("Total nodes processed:", handler.count)