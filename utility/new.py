# Creates a new blank world as binary data
#
# Layers [7]:
#   Underground - dirt, mines, rocks
#   Ground - ground tiles
#   Collisions - invisible collisions for walls, trees, etc.
#   Foreground - everything drawn above the player (drawn above walls for extra stuff)
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

import pygame
import struct
import os

pygame.init()

# Colors
BG_COLOR = (20, 20, 20)
PANEL_COLOR = (45, 45, 50)
FIELD_COLOR = (60, 60, 65)
FIELD_ACTIVE_COLOR = (70, 70, 80)
TEXT_COLOR = (220, 220, 220)
LABEL_COLOR = (160, 160, 170)
ACCENT_COLOR = (100, 140, 200)
BUTTON_COLOR = (70, 120, 180)
BUTTON_HOVER_COLOR = (90, 140, 200)
ERROR_COLOR = (200, 80, 80)

# Window setup
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 320
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('New Level')

# Fonts
font = pygame.font.SysFont('Arial', 18)
fontSmall = pygame.font.SysFont('Arial', 14)
fontTitle = pygame.font.SysFont('Arial', 24, bold=True)

class InputField:
    def __init__(self, x, y, width, height, label, maxChars=32, numeric=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.label = label
        self.text = ''
        self.active = False
        self.maxChars = maxChars
        self.numeric = numeric

    def handleEvent(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)

        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_TAB:
                return 'next'
            elif len(self.text) < self.maxChars:
                char = event.unicode
                if self.numeric:
                    if char.isdigit():
                        self.text += char
                else:
                    if char.isprintable() and char != '\t':
                        self.text += char
        return None

    def getValue(self):
        if self.numeric:
            return int(self.text) if self.text else 0
        return self.text

    def draw(self, surface):
        # Label
        labelSurface = fontSmall.render(self.label, True, LABEL_COLOR)
        surface.blit(labelSurface, (self.rect.x, self.rect.y - 22))

        # Field background
        color = FIELD_ACTIVE_COLOR if self.active else FIELD_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=2)

        # Border
        border_color = ACCENT_COLOR if self.active else (80, 80, 85)
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=2)

        # Text
        textSurface = font.render(self.text, True, TEXT_COLOR)
        textRect = textSurface.get_rect(midleft=(self.rect.x + 12, self.rect.centery))
        surface.blit(textSurface, textRect)

        # Cursor
        if self.active:
            cursorX = textRect.right + 2
            if pygame.time.get_ticks() % 1000 < 500:
                pygame.draw.line(surface, TEXT_COLOR,
                               (cursorX, self.rect.y + 8),
                               (cursorX, self.rect.bottom - 8), 2)


class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.hovered = False

    def handleEvent(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def draw(self, surface):
        color = BUTTON_HOVER_COLOR if self.hovered else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=2)

        textSurface = font.render(self.text, True, TEXT_COLOR)
        textRect = textSurface.get_rect(center=self.rect.center)
        surface.blit(textSurface, textRect)


def saveLevel(prisonName, width, height, filename):
    # Ensure filename has .map extension
    if not filename.endswith('.map'):
        filename += '.map'

    # Prepare prison name (pad to 32 bytes)
    nameBytes = prisonName.encode('utf-8')[:32]
    nameLength = len(nameBytes)
    namePadded = nameBytes.ljust(32, b'\x00')

    # Calculate layer size
    layerSize = width * height

    # Build binary data
    data = bytearray()

    # Name length (uint8)
    data.append(nameLength)

    # Prison name (32 bytes)
    data.extend(namePadded)

    # Width (uint8)
    data.append(width)

    # Height (uint8)
    data.append(height)

    # 7 layers of uint16 data (all zeros)
    for layer in range(7):
        for tile in range(layerSize):
            data.extend(struct.pack('<H', 0))  # Little-endian uint16

    # Write to file
    with open(filename, 'wb') as f:
        f.write(data)

    return filename


def main():
    clock = pygame.time.Clock()

    # Create input fields
    fieldWidth = 420
    fieldHeight = 36
    startX = 40
    startY = 80
    spacing = 70

    fields = [
        InputField(startX, startY, fieldWidth, fieldHeight,
                   'Prison Name (max 32 characters)', maxChars=32),
        InputField(startX, startY + spacing, 120, fieldHeight,
                   'Width (tiles)', maxChars=3, numeric=True),
        InputField(startX + 150, startY + spacing, 120, fieldHeight,
                   'Height (tiles)', maxChars=3, numeric=True),
    ]

    fields[0].active = True  # Start with first field active

    # Create save button
    saveButton = Button(startX, startY + spacing * 2, 120, 44, 'Save')

    # Status message
    statusMessage = ''
    statusColor = TEXT_COLOR
    statusTime = 0

    running = True
    while running:
        currentTime = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Handle field input
            for i, field in enumerate(fields):
                result = field.handleEvent(event)
                if result == 'next':
                    field.active = False
                    fields[(i + 1) % len(fields)].active = True

            # Handle save button
            if saveButton.handleEvent(event):
                prisonName = fields[0].text
                width = fields[1].getValue()
                height = fields[2].getValue()

                # Validation
                if not prisonName:
                    statusMessage = 'Please enter a prison name'
                    statusColor = ERROR_COLOR
                    statusTime = currentTime
                elif width < 1 or width > 255:
                    statusMessage = 'Width must be between 1 and 255'
                    statusColor = ERROR_COLOR
                    statusTime = currentTime
                elif height < 1 or height > 255:
                    statusMessage = 'Height must be between 1 and 255'
                    statusColor = ERROR_COLOR
                    statusTime = currentTime
                else:
                    try:
                        savedPath = saveLevel(prisonName, width, height, 'prison.map')
                        statusMessage = f'Saved: {savedPath}'
                        statusColor = ACCENT_COLOR
                        statusTime = currentTime
                    except Exception as e:
                        statusMessage = f'Error: {str(e)}'
                        statusColor = ERROR_COLOR
                        statusTime = currentTime

        # Draw
        screen.fill(BG_COLOR)

        # Title
        titleSurface = fontTitle.render('Create New Level', True, TEXT_COLOR)
        screen.blit(titleSurface, (startX, 25))

        # Draw fields
        for field in fields:
            field.draw(screen)

        # Draw button
        saveButton.draw(screen)

        # Draw status message (fade after 3 seconds)
        if statusMessage and currentTime - statusTime < 3000:
            alpha = 255 if currentTime - statusTime < 2500 else int(255 * (3000 - (currentTime - statusTime)) / 500)
            statusSurface = fontSmall.render(statusMessage, True, statusColor)
            statusSurface.set_alpha(alpha)
            screen.blit(statusSurface, (startX + 140, startY + spacing * 2 + 32))

        # Info text
        infoText = fontSmall.render('Level data will be initialized with empty tiles (all zeros)', True, LABEL_COLOR)
        screen.blit(infoText, (startX, WINDOW_HEIGHT - 35))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == '__main__':
    main()