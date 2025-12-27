
# Creates a new blank world as binary data
#
# Layers [7]:
#   Underground - dirt, mines, rocks
#   Ground - ground tiles
#   Foreground - everything drawn above the player
#   Collisions - invisible collisions for walls, trees, etc.
#   Vents
#   Roof ground - roof ground tiles, pipes
#   Roof - walls, ziplines, etc.
#
# Version 1
#
# +----------+--------+-------------------+------------------------------------------------+
# | Offset   | Size   | Type              | Description                                    |
# +==========+========+===================+================================================+
# | 0x00     | 1 B    | uint8_t           | Length of prison name (32 char max)            |
# |          |        |                   |                                                |
# +----------+--------+-------------------+------------------------------------------------+
# | 0x01     | 32 B   | char[32]          | Prison name                                    |
# |          |        |                   |                                                |
# +----------+--------+-------------------+------------------------------------------------+
# | 0x21     | 1 B    | uint8_t           | Level width                                    |
# |          |        |                   |                                                |
# +----------+--------+-------------------+------------------------------------------------+
# | 0x22     | 1 B    | uint8_t           | Level height                                   |
# |          |        |                   |                                                |
# +----------+--------+-------------------+------------------------------------------------+
# | 0x23     | -      | uint16_t[7][H][W] | Raw level data (VARIABLE SIZE)                 |
# |          |        |                   |                                                |
# +----------+--------+-------------------+------------------------------------------------+

import struct
import os

# TODO: Require defauly data such as dimensions