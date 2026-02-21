# Loads a tileset image and helps identify individual tile id
# Tile id starts at 0 in the top left, and increases to the right, wrapping once it hits the end
# (x, y) starts at (0, 0) in the top left and increases towards the bottom right

import pygame

tileSize = 16
atlasSize = 512 # Square number

tilesPerRow = atlasSize // tileSize

pygame.init()

screen = pygame.display.set_mode((atlasSize * 1.0625, (atlasSize * 1.0625) + (11 * tileSize)))
pygame.display.set_caption('Atlas Helper')

atlas = pygame.image.load('assets/tileset/prison0/ground_tiles.png').convert_alpha()
atlasOffset = int (atlasSize * 0.03125)

# Theme colors
BG_COLOR = (20, 20, 20)
TEXT_COLOR = (220, 220, 220)
LABEL_COLOR = (160, 160, 170)
ACCENT_COLOR = (100, 140, 200)
HIGHLIGHT_COLOR = (50, 50, 70)
SELECTED_COLOR = (255, 0, 0)

idOffset = 1

# Fonts
font = pygame.font.SysFont('Arial', 18)

highlightedID = -1
selectedID = -1

def drawCheckerboard(surface, rect, cellSize = 8, color1 = (70, 70, 70), color2 = (90, 90, 90)):
    
    x0, y0, w, h = rect
    for y in range(0, h, cellSize):
        for x in range(0, w, cellSize):
            color = color1 if (x // cellSize + y // cellSize) % 2 == 0 else color2
            pygame.draw.rect(
                surface,
                color,
                (x0 + x, y0 + y, cellSize, cellSize)
            )

def drawStripedBorder(surface, rect, stripeSize = 16, thickness = 2, color1 = (255, 215, 0), color2 = (0, 0, 0)):
    
    x, y, w, h = rect
    colors = (color1, color2)

    # Top and bottom edges (left to right)
    for i in range(0, w, stripeSize):
        idx = (i // stripeSize) % 2
        color = colors[idx]

        pygame.draw.rect(surface, color, (x + i, y - thickness, stripeSize, thickness))
        pygame.draw.rect(surface, color, (x + i, y + h, stripeSize, thickness))

    # Left and right edges (top to bottom)
    for i in range(0, h, stripeSize):
        idx = (i // stripeSize) % 2
        color = colors[idx]

        pygame.draw.rect(surface, color, (x - thickness, y + i, thickness, stripeSize))
        pygame.draw.rect(surface, color, (x + w, y + i, thickness, stripeSize))

    # Add yellow corners at intersection
    def stripeColor(offset):
        return colors[(offset // stripeSize) % 2]
    
    # Top-left
    if stripeColor(0) == color1 and stripeColor(0) == color1:
        pygame.draw.rect(surface, color1, (x - thickness, y - thickness, thickness, thickness))

    # Top-right
    if stripeColor(w - 1) == color1 and stripeColor(0) == color1:
        pygame.draw.rect(surface, color1, (x + w, y - thickness, thickness, thickness))

    # Bottom-left
    if stripeColor(0) == color1 and stripeColor(h - 1) == color1:
        pygame.draw.rect(surface, color1, (x - thickness, y + h, thickness, thickness))

    # Bottom-right
    if stripeColor(w - 1) == color1 and stripeColor(h - 1) == color1:
        pygame.draw.rect(surface, color1, (x + w, y + h, thickness, thickness))

run = True
while run:

    # Close window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Left click
                if selectedID == highlightedID:
                    selectedID = -1
                else:
                    selectedID = highlightedID
        elif event.type == pygame.KEYDOWN and selectedID != -1:
            tileX = selectedID % tilesPerRow
            tileY = selectedID // tilesPerRow

            if event.key == pygame.K_LEFT:
                tileX -= 1
            elif event.key == pygame.K_RIGHT:
                tileX += 1
            elif event.key == pygame.K_UP:
                tileY -= 1
            elif event.key == pygame.K_DOWN:
                tileY += 1

            tileX = max(0, min(tileX, tilesPerRow - 1))
            tileY = max(0, min(tileY, tilesPerRow - 1))

            selectedID = (tileY * tilesPerRow) + tileX

    screen.fill(BG_COLOR)

    # Background
    drawCheckerboard(screen, (atlasOffset, atlasOffset, atlasSize, atlasSize), cellSize = 8)
    drawCheckerboard(screen, (atlasOffset, atlasSize + (2 * atlasOffset) + tileSize, 9 * tileSize, 9 * tileSize), cellSize = 8) # Preview

    drawStripedBorder(screen, (atlasOffset, atlasOffset, atlasSize, atlasSize), stripeSize = 16, thickness = 2)
    drawStripedBorder(screen, (atlasOffset, atlasSize + (2 * atlasOffset) + tileSize, 9 * tileSize, 9 * tileSize), stripeSize = 16, thickness = 2) # Preview

    # Draw tileset
    screen.blit(atlas, (atlasOffset, atlasOffset))

    # Cursor
    mouseX, mouseY = pygame.mouse.get_pos()
    localX = mouseX - atlasOffset
    localY = mouseY - atlasOffset

    if 0 <= localX < atlasSize and 0 <= localY < atlasSize:
        tileX = localX // tileSize
        tileY = localY // tileSize

        highlightedID = tileY * tilesPerRow + tileX # ID of highlighted tile

        highlightRect = pygame.Rect(atlasOffset + (tileX * tileSize), atlasOffset + (tileY * tileSize), tileSize, tileSize)
        pygame.draw.rect(screen, HIGHLIGHT_COLOR, highlightRect, 1) # Cursor highlight

    if selectedID != -1:
        highlightRect = pygame.Rect(atlasOffset + (selectedID % tilesPerRow * tileSize), atlasOffset + (selectedID // tilesPerRow * tileSize), tileSize, tileSize)
        pygame.draw.rect(screen, SELECTED_COLOR, highlightRect, 1) # Selected highlight

    # 3x3 preview
    idx = highlightedID
    if selectedID != -1:
        idx = selectedID
    if idx != -1:
        preview = pygame.Surface((3 * tileSize, 3 * tileSize), pygame.SRCALPHA)
        centerX = idx % tilesPerRow
        centerY = idx // tilesPerRow

        for dy in range(-1, 2):
            for dx in range(-1, 2):
                tx = centerX + dx
                ty = centerY + dy

                if 0 <= tx < tilesPerRow and 0 <= ty < tilesPerRow:
                    srcRect = pygame.Rect(
                        tx * tileSize,
                        ty * tileSize,
                        tileSize,
                        tileSize
                    )

                    destPos = (
                        (dx + 1) * tileSize,
                        (dy + 1) * tileSize
                    )

                    preview.blit(atlas, destPos, srcRect)
        
        screen.blit(
            pygame.transform.scale(preview, (9 * tileSize, 9 * tileSize)),
            (atlasOffset, atlasSize + (2 * atlasOffset) + tileSize)
        )

    thickness = 1

    # 3x3 grid - horizontal lines
    pygame.draw.line(
        screen,
        HIGHLIGHT_COLOR,
        (atlasOffset + (3 * tileSize), atlasSize + (2 * atlasOffset) + tileSize),
        (atlasOffset + (3 * tileSize), atlasSize + (2 * atlasOffset) + (10 * tileSize)),
        thickness
    )

    pygame.draw.line(
        screen,
        HIGHLIGHT_COLOR,
        (atlasOffset + (6 * tileSize), atlasSize + (2 * atlasOffset) + tileSize),
        (atlasOffset + (6 * tileSize), atlasSize + (2 * atlasOffset) + (10 * tileSize)),
        thickness
    )

    # 3x3 grid - vertical lines
    pygame.draw.line(
        screen,
        HIGHLIGHT_COLOR,
        (atlasOffset, atlasSize + (2 * atlasOffset) + (4 * tileSize)),
        (atlasOffset + (9 * tileSize), atlasSize + (2 * atlasOffset) + (4 * tileSize)),
        thickness
    )
    
    pygame.draw.line(
        screen,
        HIGHLIGHT_COLOR,
        (atlasOffset, atlasSize + (2 * atlasOffset) + (7 * tileSize)),
        (atlasOffset + (9 * tileSize), atlasSize + (2 * atlasOffset) + (7 * tileSize)),
        thickness
    )

    # Preview info
    idLabel = font.render(f"ID: {idx + idOffset}", True, TEXT_COLOR)
    xyLabel = font.render(f"X: {idx % tilesPerRow}, Y: {idx // tilesPerRow}", True, TEXT_COLOR)

    screen.blit(idLabel, (atlasOffset + (10 * tileSize), atlasSize + (2 * atlasOffset) + tileSize))
    screen.blit(xyLabel, (atlasOffset + (10 * tileSize), atlasSize + (2 * atlasOffset) + tileSize + 22))
    
    # Redraw
    pygame.display.update()

pygame.quit()