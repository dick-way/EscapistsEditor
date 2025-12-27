# Palette information is helpful to easily make clean, polished levels.
# Since different prisons have different counts/kinds of palettes,
# There will be a unique palette information for each prison.
# Keep in mind, this only effects the level editor, not the game
#
# There are 16 unique types of tiles you can imagine in a base palette.
# Break each tile into a 2x2 matrix:   Ex. [1 1]
#                                          [0 0]
# This could represent a tile with the top half being grass and the bottom dirt.
# The idea is that there are two mediums that each palette connects,
# But they don't have to be completely different.
# These palettes also apply for indoor tiles to give a little variation
# And display a "dirty" floor.
#
# With the mediums being distinguished by a 1 or a 0, that leaves 16 total (2^4) tiles
# Obvisouly, we may want some variation, but these 16 types allow us to group them together
#
# This first item in the paletteData array contains the outline for creating a paltte to use
# The data represents this base tileset;
#
#           [0, 0]   [0, 1]   [1, 0]   [0, 0]
#           [1, 0]   [0, 1]   [1, 1]   [1, 1]
#
#           [1, 0]   [0, 1]   [1, 1]   [1, 1]
#           [0, 1]   [1, 1]   [1, 1]   [1, 0]
#
#           [0, 1]   [1, 1]   [1, 1]   [1, 0]
#           [0, 0]   [0, 0]   [0, 1]   [1, 0]
#
#           [0, 0]   [0, 0]   [0, 1]   [1, 0]
#           [0, 0]   [0, 1]   [1, 0]   [0, 0]
#
# Or more clearly:
#
#           □ □   □ ■   ■ □   □ □
#           ■ □   □ ■   ■ ■   ■ ■
#
#           ■ □   □ ■   ■ ■   ■ ■
#           □ ■   ■ ■   ■ ■   ■ □
#
#           □ ■   ■ ■   ■ ■   ■ □
#           □ □   □ □   □ ■   ■ □
#
#           □ □   □ □   □ ■   ■ □
#           □ □   □ ■   ■ □   □ □
#
# If you take a look at the tilesets, you will notice that the tiles don't match this pattern.
# The other items in this array connect the tile on the spritesheet to the shape of that tile
# This allows the level editor to understand what the pieces look like and make smooth connections
#
# The tile types such as [1, 0] or [0, 1] are cut from the meta palleteData, since they do not exist in the game
#                        [0, 1]    [1, 0]
#
# The tile types for palette type 1 include 4 extra subarays that store the four 2x2 corner slopes
#
# Tile id starts at 0 from the top left and goes right, each tile is 16x16 pixels
#
# Alignment ID:
#   A single number identifying the top-left tile of that palette
#
# Palette Type:
#   0: Simplest palette with 2 mediums, 2 variations for each edge piece
#   1: Same as 0, but contains variated corner sloped tiles (extra 4x4 diamond in tileset)

paletteData = [

    # 0 - Tile Data
    [
        
        # Mapping to tileset - Base (δηλαδή, add the digit of the other items in paletteData to fully map tiles of that palette)
        # Palette Type 0:
        [[2], [32, 130], [160], [1, 161], [162], [33], [96], [64], [65, 97], [98], [128], [129], [0], [66]],

        # Palette Type 1:
        [[2], [32, 130], [160], [1, 161], [162], [33], [96], [64], [65, 97], [98], [128], [129], [0], [66], [67, 68, 99, 100], [69, 70, 101, 102], [131, 132, 163, 164], [133, 134, 165, 166]],

        # Tile Outline - Physical 2x2 matrix definition of tile shape
        [[0, 0, 1, 0], [0, 1, 0, 1], [1, 0, 1, 1], [0, 0, 1, 1], [0, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 0], [0, 1, 0, 0], [1, 1, 0, 0], [1, 1, 0, 1], [1, 0, 1, 0], [0, 0, 0, 0], [0, 0, 0, 1], [1, 0, 0, 0]]
     
    ],

    # 1 - Center Perks
    [
        # Grass on asphalt
        [0, 1], # [Alignment ID, Palette Type]

        # Foliage on grass
        [192, 1],

        # Grass on water
        [384, 1],

        # Deep water on water
        [576, 0]
    ],

    # 2 - Stalag Flucht
    [
        # Snow on dirt
        [0, 0],

        # Foliage on snow
        [192, 0]
    ],

    # 3 - Shankton State Pen
    [
        # Grass on dirt
        [0, 0],

        # Foliage on grass
        [192, 0]
    ],

    # 4 - Jungle Compound
    [
        # Grass on dirt
        [0, 0],

        # Foliage on grass
        [192, 0],

        # Foliage on dirt
        [3, 0],

        # Dark foliage on foliage
        [195, 0],

        # Dark foliage on dirt
        [6, 0],

        # Soil on dirt
        [198, 0]
    ],

    # 5 - San Pancho
    [
        # ?
        [0, 1],

        [192, 1],

        [384, 0]
    ],

    # 6 - HMP Irongate
    [
        # Grass on asphalt
        [0, 1],

        # Foliage on grass
        [192, 1],

        # Grass on water
        [384, 1],

        # Deep water on water
        [576, 0]
    ]

]