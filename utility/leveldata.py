# Handles loading, saving, and editing of level data from .map files.
#
# id 0         : Always NULL tile
# id 1-1024    : Prison tileset
# id 1025-     :

import struct

class LevelData:

    def __init__(self):
        self.prisonName = ""
        self.width = 0
        self.height = 0
        # 3D list: layers[layer][y][x]
        self.layers = []

    def load(self, filename):
        with open(filename, 'rb') as f:
            # Read header
            nameLength = struct.unpack('B', f.read(1))[0]
            nameBytes = f.read(32)
            self.prisonName = nameBytes[:nameLength].decode('utf-8')

            self.width = struct.unpack('B', f.read(1))[0]
            self.height = struct.unpack('B', f.read(1))[0]

            # Read 7 layers
            self.layers = []
            for layer in range(7):
                layerData = []
                for y in range(self.height):
                    row = []
                    for x in range(self.width):
                        tileID = struct.unpack('<H', f.read(2))[0]
                        row.append(tileID)
                    layerData.append(row)
                self.layers.append(layerData)

    def save(self, filename):
        # Ensure filename has .map extension
        if not filename.endswith('.map'):
            filename += '.map'

        # Prepare prison name (pad to 32 bytes)
        nameBytes = self.prisonName.encode('utf-8')[:32]
        nameLength = len(nameBytes)
        namePadded = nameBytes.ljust(32, b'\x00')

        # Build binary data
        data = bytearray()
        data.append(nameLength)
        data.extend(namePadded)
        data.append(self.width)
        data.append(self.height)

        # Write all 7 layers
        for layer in self.layers:
            for row in layer:
                for tileID in row:
                    data.extend(struct.pack('<H', tileID))

        # Write to file
        with open(filename, 'wb') as f:
            f.write(data)

    def getTile(self, layer, x, y):
        if 0 <= layer < 7 and 0 <= y < self.height and 0 <= x < self.width:
            return self.layers[layer][y][x]
        return 0

    def setTile(self, layer, x, y, tileID):
        if 0 <= layer < 7 and 0 <= y < self.height and 0 <= x < self.width:
            self.layers[layer][y][x] = tileID

    def createBlank(self, prisonName, width, height):
        self.prisonName = prisonName
        self.width = width
        self.height = height

        # Create 7 layers of empty tiles
        self.layers = []
        for layer in range(7):
            layerData = []
            for y in range(height):
                row = [0] * width
                layerData.append(row)
            self.layers.append(layerData)
