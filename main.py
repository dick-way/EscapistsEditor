import pygame

import palette

from smoothscroller import SmoothScroller

pygame.init()

screenWidth = 1600
screenHeight = 950

tileSize = 16

screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption('The Escapists Level Editor')

temp = pygame.image.load('reference.png').convert_alpha()

mapWidth = 108 # TODO: Tile count, from .bin data
mapHeight = 88

# Create and center map window
mapWindowWidth = 1152
mapWindowHeight = 864

mapRect = pygame.Rect(0, 0, mapWindowWidth, mapWindowHeight)
mapSurface = pygame.Surface(mapRect.size) # TODO: Edge indicators

zoomHorizontal = 36 # This number is the number of tiles horizontally visible in the window, preferably common divisors of mapWindowWidth and mapWindowHeight that can display in the window ratio (3:4)
                    #   [4, 8, 12, 16, 24, 32, 36, 48, 72, 96, 144, 288]
zoomVertical = int(zoomHorizontal * (3/4))

scrollXMax = (mapWidth - zoomHorizontal) * tileSize
scrollYMax = (mapHeight - (zoomVertical)) * tileSize

screenRect = screen.get_rect()
mapRect.center = screenRect.center

def drawMapWindow():
    
    relativeTileSize = mapWindowWidth // zoomHorizontal

    for x in range(zoomHorizontal):
        pygame.draw.line(mapSurface, (255, 255, 255), ((x * relativeTileSize) + ((scroller.scrollX % tileSize) * (relativeTileSize / tileSize)), 0), ((x * relativeTileSize) + ((scroller.scrollX % tileSize) * (relativeTileSize / tileSize)), mapWindowHeight), 1)
    
    for y in range(zoomVertical):
        pygame.draw.line(mapSurface, (255, 255, 255), (0, (y * relativeTileSize) + ((scroller.scrollY % tileSize) * (relativeTileSize / tileSize))), (mapWindowWidth, (y * relativeTileSize) + ((scroller.scrollY % tileSize) * (relativeTileSize / tileSize))), 1)

scroller = SmoothScroller(scrollXMax, scrollYMax)
clock = pygame.time.Clock()

run = True
while run:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.MOUSEWHEEL:
            scroller.handleScroll(-event.x, event.y)
    
    scroller.update()

    mapSurface.fill((0, 0, 0))

    # Crop a section from temp
    croppedImage = temp.subsurface(pygame.Rect(int(scroller.getRealOffsetX()), int(scroller.getRealOffsetY()), int(tileSize * (zoomHorizontal)), int(tileSize * (zoomVertical))))

    # Scale to exact dimensions
    scaledImage = pygame.transform.scale(croppedImage, (1152, 864))

    # Draw to mapSurface
    mapSurface.blit(scaledImage, (0, 0))

    # Map window
    drawMapWindow()
    
    screen.blit(mapSurface, mapRect.topleft)
    pygame.draw.rect(screen, (255, 255, 255), mapRect, 2)

    # Draw windows, handle input
    pygame.display.flip()

    clock.tick(60)

pygame.quit()