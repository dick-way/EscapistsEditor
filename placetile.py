import random

import numpy
from info import palette

# If manual != 1, it will output a 3x3 around the center tile to connect 2 mediums
# Otherwise, it will replace the sole center tile and always overwrite (manual editing)
def placeTile(level, tileX, tileY, manual):

    if manual == 1:
        # Manual tile overwrite
        level.setTile(1, tileX, tileY, 0)

    else:
    
        # Palette builder
        for j in range(0, 4):
            # j controls the 4 2x2 palette calculations
            if paletteSpace(level, tileX + (j % 2), tileY + (j // 2)):
                for i in range(0, 4):
                    # i controls each inner 2x2
                    level.setTile(1, tileX + (i % 2) + (j % 2) - 1, tileY + (i // 2) + (j // 2) - 1, paletteTile(level, tileX + (i % 2) + (j % 2) - 1, tileY + (i // 2) + (j // 2) - 1, i))

def paletteTile(level, tileX, tileY, corner):
    
    alignmentID = palette.paletteData[palette.selected[0]][palette.selected[1]][0]

    done = False
    tile = [level.getTile(1, tileX, tileY)]

    for i in palette.identicalTiles[palette.selected[0] - 1]:
        for j in i:
            if tile[0] == j:
                tile = i
                done = True
                break
        if done:
            break
    
    groundIndex = -1
    for index, i in enumerate(palette.paletteData[0][0]):
        for j in i:
            for k in tile:
                if alignmentID + j == k: # Alignment ID + offset == tile
                    groundIndex = index
            if groundIndex != -1:
                break
        if groundIndex != -1:
                break

    tile0 = numpy.array(palette.paletteData[0][2][groundIndex])
    tile1 = numpy.array([0, 0, 0, 0])
    tile1[3 - corner] = 1

    # Combine tile data together
    tileResult = tile0 | tile1

    if palette.selected[2] == 1:
        # Inversion
        tileResult = tile0 & ~tile1

    # Don't replace identical tiles
    if (tile0 == tileResult).all():
        return -1

    for index, item in enumerate(palette.paletteData[0][2]):
        if (tileResult == item).all():
            # Find match to combined tile to place
            return alignmentID + random.choice(palette.paletteData[0][1][index]) # Put variated tiles in here: random.randint(-1, 0)
    
    print(f"tilex: {tileX} tiley: {tileY} ({alignmentID + palette.paletteData[0][1][11][0]})")

    # Unable to find a match, glitched tile
    return alignmentID + palette.paletteData[0][1][11][0]

def paletteSpace(level, tileX, tileY):

    # Checks 2x2 space to overwrite medium
    for x in range(-1, 1):
        for y in range(-1, 1):
            
            # Check 2x2 overwrite space
            if inTileset(level.getTile(1, tileX + x, tileY + y), palette.paletteData[palette.selected[0]][palette.selected[1]]) == False:
                return False
    return True

def inTileset(tileID, info): # Info: [alignmentID, paletteType]

    # Check for identical tiles
    done = False
    tile = [tileID]
    for i in palette.identicalTiles[palette.selected[0] - 1]:
        for j in i:
            if tile[0] == j:
                tile = i
                done = True
                break
        if done:
            break

    # Check if the tile is in tileset
    for i in palette.paletteData[0][info[1]]:
        for j in i:
            for k in tile:
                if k == info[0] + j:
                    return True

    return False