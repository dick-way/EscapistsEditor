import pygame

from info import palette
from smoothscroller import SmoothScroller

pygame.init()

# Theme colors
bgColor = (30, 30, 35)
textColor = (220, 220, 220)
labelColor = (160, 160, 170)
accentColor = (100, 140, 200)

# Fonts
font = pygame.font.SysFont('Arial', 18)
fontSmall = pygame.font.SysFont('Arial', 14)
fontTitle = pygame.font.SysFont('Arial', 24, bold=True)

screenWidth = 1600
screenHeight = 950

tileSize = 16

screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption('The Escapists Level Editor')

mapWidth = 108 # TODO: Tile count, from .bin data
mapHeight = 88

# Create and center map window
mapWindowWidth = 1152
mapWindowHeight = 864

mapWindowRect = pygame.Rect(0, 0, mapWindowWidth, mapWindowHeight)
mapWindowSurface = pygame.Surface(mapWindowRect.size) # TODO: Edge indicators

zoomLevels = [4, 8, 12, 16, 24, 32, 36, 48, 72]
zoomIndex = 4
lastScrollTime = 0
scrollCooldown = 200

zoomHorizontal = zoomLevels[zoomIndex]
zoomVertical = int(zoomHorizontal * (3/4))

relativeTileSize = mapWindowWidth // zoomHorizontal

scrollXMax = (mapWidth - zoomHorizontal) * tileSize
scrollYMax = (mapHeight - zoomVertical) * tileSize

screenRect = screen.get_rect()
mapWindowRect.center = screenRect.center

# TEMP reference image
# temp = pygame.image.load('reference.png').convert_alpha()

def setZoom(index):

    global zoomIndex, zoomHorizontal, zoomVertical, scrollXMax, scrollYMax, relativeTileSize

    # Keep zoomIndex in bounds
    zoomIndex = max(0, min(len(zoomLevels) - 1, index))

    zoomHorizontal = zoomLevels[zoomIndex]
    zoomVertical = int(zoomLevels[zoomIndex] * (3/4))

    # Update scroll bounds
    scrollXMax = (mapWidth - zoomHorizontal) * tileSize
    scrollYMax = (mapHeight - zoomVertical) * tileSize

    scroller.setScrollBounds(scrollXMax, scrollYMax)

    # Update relativeTileSize
    relativeTileSize = mapWindowWidth // zoomHorizontal

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

def drawMapWindow():

    for x in range(zoomHorizontal):
        pygame.draw.line(mapWindowSurface, (255, 255, 255), ((x * relativeTileSize) + ((scroller.scrollX % tileSize) * (relativeTileSize / tileSize)), 0), ((x * relativeTileSize) + ((scroller.scrollX % tileSize) * (relativeTileSize / tileSize)), mapWindowHeight), 1)
    
    for y in range(zoomVertical):
        pygame.draw.line(mapWindowSurface, (255, 255, 255), (0, (y * relativeTileSize) + ((scroller.scrollY % tileSize) * (relativeTileSize / tileSize))), (mapWindowWidth, (y * relativeTileSize) + ((scroller.scrollY % tileSize) * (relativeTileSize / tileSize))), 1)

scroller = SmoothScroller(scrollXMax, scrollYMax)
clock = pygame.time.Clock()

run = True
while run:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        # Handle mouse wheel with shift key
        elif event.type == pygame.MOUSEWHEEL:
            mousePos = pygame.mouse.get_pos()
            if mapWindowRect.collidepoint(mousePos):
                keys = pygame.key.get_mods()
                if keys & pygame.KMOD_SHIFT:
                    #Shift is held, adjust zoom
                    currentTime = pygame.time.get_ticks()
                    if currentTime - lastScrollTime > scrollCooldown:
                        lastScrollTime = currentTime

                        # Calculate mouse position relative to map window
                        mouseRelX = mousePos[0] - mapWindowRect.x
                        mouseRelY = mousePos[1] - mapWindowRect.y

                        # Calculate world position under mouse before zoom
                        worldX = scroller.getRealOffsetX() + (mouseRelX / relativeTileSize) * tileSize
                        worldY = scroller.getRealOffsetY() + (mouseRelY / relativeTileSize) * tileSize

                        # Apply zoom
                        if event.y > 0:
                            setZoom(zoomIndex + 1)
                        elif event.y < 0:
                            setZoom(zoomIndex - 1)

                        # Calculate new scroll position to keep world point under mouse
                        newScrollX = scrollXMax - worldX + (mouseRelX / relativeTileSize) * tileSize
                        newScrollY = scrollYMax - worldY + (mouseRelY / relativeTileSize) * tileSize

                        # Clamp and set scroll position
                        scroller.scrollX = max(0, min(newScrollX, scrollXMax))
                        scroller.scrollY = max(0, min(newScrollY, scrollYMax))

                        # Zero out velocity to prevent drift
                        scroller.velocityX = 0
                        scroller.velocityY = 0
                else:
                    # Shift not held - handle panning (your existing code)
                    scroller.handleScroll(-event.x, event.y)
    
    scroller.update()

    screen.fill(bgColor)
    mapWindowSurface.fill((0, 0, 0))

    # TEMP Crop a section from temp
    # croppedImage = temp.subsurface(pygame.Rect(int(scroller.getRealOffsetX()), int(scroller.getRealOffsetY()), int(tileSize * (zoomHorizontal)), int(tileSize * (zoomVertical))))
    # TEMP Scale to exact dimensions
    # scaledImage = pygame.transform.scale(croppedImage, (1152, 864))
    # TEMP Draw to mapWindowSurface
    # mapWindowSurface.blit(scaledImage, (0, 0))

    # Map window
    drawCheckerboard(mapWindowSurface, mapWindowSurface.get_rect())

    drawMapWindow()
    
    screen.blit(mapWindowSurface, mapWindowRect.topleft)
    pygame.draw.rect(screen, (255, 255, 255), mapWindowRect, 2)

    # Draw windows, handle input
    pygame.display.flip()

    clock.tick(60)

pygame.quit()