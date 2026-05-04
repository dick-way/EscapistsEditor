import pygame
import subprocess
import sys
import os

# from info import palette
from smoothscroller import SmoothScroller
from utility.leveldata import LevelData
from placetile import placeTile
from info import palette

# macOS native menu bar support
menuActions = [] # Queue for menu actions

try:
    from Foundation import NSObject
    from AppKit import NSApplication, NSMenu, NSMenuItem
    from PyObjCTools import AppHelper

    class MenuDelegate(NSObject):
        def newLevel_(self, sender):
            menuActions.append('newLevel')
        def saveLevel_(self, sender):
            menuActions.append('saveLevel')
        def reloadLevel_(self, sender):
            menuActions.append('reloadLevel')

        def setZoom0_(self, sender):
            menuActions.append(('zoom', 0))
        def setZoom1_(self, sender):
            menuActions.append(('zoom', 1))
        def setZoom2_(self, sender):
            menuActions.append(('zoom', 2))
        def setZoom3_(self, sender):
            menuActions.append(('zoom', 3))
        def setZoom4_(self, sender):
            menuActions.append(('zoom', 4))
        def setZoom5_(self, sender):
            menuActions.append(('zoom', 5))
        def setZoom6_(self, sender):
            menuActions.append(('zoom', 6))
        def setZoom7_(self, sender):
            menuActions.append(('zoom', 7))
        def setZoom8_(self, sender):
            menuActions.append(('zoom', 8))

    def setupMacMenus(zoomLevelsList):
        app = NSApplication.sharedApplication()

        delegate = MenuDelegate.alloc().init()

        # Get the main menu bar
        mainMenu = NSMenu.alloc().init()
        app.setMainMenu_(mainMenu)

        # App menu (required)
        appMenuItem = NSMenuItem.alloc().init()
        mainMenu.addItem_(appMenuItem)
        appMenu = NSMenu.alloc().initWithTitle_('The Escapists Level Editor')
        appMenuItem.setSubmenu_(appMenu)

        # File menu
        fileMenuItem = NSMenuItem.alloc().init()
        mainMenu.addItem_(fileMenuItem)
        fileMenu = NSMenu.alloc().initWithTitle_('File')
        fileMenuItem.setSubmenu_(fileMenu)

        # File > New Level
        newLevelItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('New Level', 'newLevel:', 'n')
        newLevelItem.setTarget_(delegate)
        fileMenu.addItem_(newLevelItem)

        # File > Save
        saveLevelItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Save', 'saveLevel:', 's')
        saveLevelItem.setTarget_(delegate)
        fileMenu.addItem_(saveLevelItem)

        # File > Reload
        reloadLevelItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Reload','reloadLevel: ', 'r')
        reloadLevelItem.setTarget_(delegate)
        fileMenu.addItem_(reloadLevelItem)

        # Zoom menu
        zoomMenuItem = NSMenuItem.alloc().init()
        mainMenu.addItem_(zoomMenuItem)
        zoomMenu = NSMenu.alloc().initWithTitle_('Zoom')
        zoomMenuItem.setSubmenu_(zoomMenu)

        # Zoom level items
        zoomSelectors = [
            'setZoom0:', 'setZoom1:', 'setZoom2:', 'setZoom3:', 'setZoom4:',
            'setZoom5:', 'setZoom6:', 'setZoom7:', 'setZoom8:'
        ]
        for i, level in enumerate(zoomLevelsList):
            title = f'{level}'
            item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(title, zoomSelectors[i], '')
            item.setTarget_(delegate)
            zoomMenu.addItem_(item)

        # Return delegate to keep it alive
        return delegate

    hasMacMenus = True
except ImportError:
    hasMacMenus = False
    def setupMacMenus(zoomLevelsList):
        pass

pygame.init()

# Theme colors
BG_COLOR = (20, 20, 20)
TEXT_COLOR = (220, 220, 220)
LABEL_COLOR = (160, 160, 170)
ACCENT_COLOR = (100, 140, 200)

# Fonts
font = pygame.font.SysFont('Arial', 18)
fontSmall = pygame.font.SysFont('Arial', 14)
fontTitle = pygame.font.SysFont('Arial', 24, bold=True)

screenWidth = 1600
screenHeight = 874

tileSize = 16

screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption('The Escapists Level Editor')

mapWidth = 96 # TODO: Tile count, from .map data
mapHeight = 94

drawGridLines = True

# Create and center map window
mapWindowWidth = 1152
mapWindowHeight = 864

mapWindowRect = pygame.Rect(0, 0, mapWindowWidth, mapWindowHeight)
mapWindowSurface = pygame.Surface(mapWindowRect.size)

zoomLevels = [4, 8, 12, 16, 24, 32, 36, 48, 72]
zoomIndex = 4
lastScrollTime = 0
scrollCooldown = 150

# Setup macOS menus
scriptDir = os.path.dirname(os.path.abspath(__file__))
menuDelegate = setupMacMenus(zoomLevels)

zoomHorizontal = zoomLevels[zoomIndex]
zoomVertical = int(zoomHorizontal * (3/4))

relativeTileSize = mapWindowWidth // zoomHorizontal

scrollXMax = (mapWidth - zoomHorizontal) * tileSize
scrollYMax = (mapHeight - zoomVertical) * tileSize

spacePanning = False
panningRelativePos = (0, 0)
panningRelativeScroll = (0, 0)

screenRect = screen.get_rect()
mapWindowRect.center = screenRect.center

selectedTileX = -1
selectedTileY = -1

font = pygame.font.SysFont('Arial', 12)

selectedTileset = pygame.image.load('assets/tileset/prison0/ground_tiles.png').convert_alpha() # Contains tiles 1 - 1024

level = LevelData()
level.load('prison.map') # Load map to edit

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

def getTileFromSet(image, idOffset, id):

    width = image.get_width() # Image should be square
    tiles = (width // tileSize)

    if id + idOffset < 0:
        return 0

    x = ((id + idOffset) % tiles) * 16
    y = ((id + idOffset) // tiles) * 16

    tile = image.subsurface(x, y, 16, 16)

    return tile

def XYFromID(image, id):

    width = image.get_width() // tileSize

    return (id % width, id // width)

def IDFromXY(image, point):
    return 0

def drawMapWindow():

    layer = 1

    for x in range(-1, zoomHorizontal):
        for y in range(-1, zoomVertical):
            # Calculate world tile position accounting for fractional scroll offset
            worldTileX = (scroller.getRealOffsetX() + (scroller.scrollX % tileSize)) // tileSize + x
            worldTileY = (scroller.getRealOffsetY() + (scroller.scrollY % tileSize)) // tileSize + y

            # Read from data and draw tiles
            tileImage = getTileFromSet(selectedTileset, -1, level.getTile(layer, worldTileX, worldTileY))

            if tileImage != 0:
                mapWindowSurface.blit(pygame.transform.scale(tileImage, (relativeTileSize, relativeTileSize)), ((x * relativeTileSize) + ((scroller.scrollX % tileSize) * (relativeTileSize / tileSize)), (y * relativeTileSize) + ((scroller.scrollY % tileSize) * (relativeTileSize / tileSize))))

    if drawGridLines:

        for x in range(zoomHorizontal):
            pygame.draw.line(mapWindowSurface, (255, 255, 255), ((x * relativeTileSize) + ((scroller.scrollX % tileSize) * (relativeTileSize / tileSize)), 0), ((x * relativeTileSize) + ((scroller.scrollX % tileSize) * (relativeTileSize / tileSize)), mapWindowHeight), 1)
        
        for y in range(zoomVertical):
            pygame.draw.line(mapWindowSurface, (255, 255, 255), (0, (y * relativeTileSize) + ((scroller.scrollY % tileSize) * (relativeTileSize / tileSize))), (mapWindowWidth, (y * relativeTileSize) + ((scroller.scrollY % tileSize) * (relativeTileSize / tileSize))), 1)

scroller = SmoothScroller(scrollXMax, scrollYMax)
clock = pygame.time.Clock()

mouseHeld = False

# Selection Panel
panelWidth = (screenWidth - mapWindowWidth) // 2
leftBound = panelWidth + mapWindowWidth

selectionTileWidth = 80
selectionTileSpacing = (panelWidth - (2 * selectionTileWidth)) // 3
selectionPanelHeading = 22

selectionTileBorder = 1

selectionInversion = list()
for i in range(0, len(palette.paletteData[palette.selected[0]])):
    selectionInversion.append(0)

run = True
while run:

    mousePos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        # Space panning
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                spacePanning = True
                panningRelativePos = pygame.mouse.get_pos()
                panningRelativeScroll = (scroller.scrollX, scroller.scrollY)
        
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                spacePanning = False

        # Handle mouse wheel with shift key
        elif event.type == pygame.MOUSEWHEEL:
            if mapWindowRect.collidepoint(mousePos):
                keys = pygame.key.get_mods()
                if keys & pygame.KMOD_SHIFT:

                    # Shift is held, adjust zoom (not while panning)
                    currentTime = pygame.time.get_ticks()
                    if currentTime - lastScrollTime > scrollCooldown and not spacePanning:
                        lastScrollTime = currentTime

                        # Calculate mouse position relative to map window
                        mouseRelX = mousePos[0] - mapWindowRect.x
                        mouseRelY = mousePos[1] - mapWindowRect.y

                        # Calculate world position under mouse BEFORE zoom (using old relativeTileSize)
                        worldX = scroller.getRealOffsetX() + (mouseRelX / relativeTileSize) * tileSize
                        worldY = scroller.getRealOffsetY() + (mouseRelY / relativeTileSize) * tileSize

                        # Save old zoom index to check if zoom actually changes
                        oldZoomIndex = zoomIndex

                        # Apply zoom
                        if event.y > 0:
                            setZoom(zoomIndex + 1)
                        elif event.y < 0:
                            setZoom(zoomIndex - 1)
                        elif event.y == 0:
                            # Fixes mouse converting vertical scroll to horizontal scroll
                            if event.x < 0:
                                setZoom(zoomIndex + 1)
                            elif event.x > 0:
                                setZoom(zoomIndex - 1)

                        # Only adjust scroll if zoom actually changed
                        if zoomIndex != oldZoomIndex:
                            # Calculate new scroll position to keep world point under mouse (using new relativeTileSize)
                            newScrollX = scrollXMax - worldX + (mouseRelX / relativeTileSize) * tileSize
                            newScrollY = scrollYMax - worldY + (mouseRelY / relativeTileSize) * tileSize

                            # Clamp and set scroll position
                            scroller.scrollX = max(0, min(newScrollX, scrollXMax))
                            scroller.scrollY = max(0, min(newScrollY, scrollYMax))

                            # Zero out velocity to prevent drift
                            scroller.velocityX = 0
                            scroller.velocityY = 0
                    
                else:
                    # Shift not held
                    scroller.handleScroll(-event.x, event.y)
            
        # Click
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouseHeld = True

            # Update selection in panel            
            for i in range(0, len(palette.paletteData[palette.selected[0]])):

                x = i % 2
                y = i // 2

                if mousePos[0] > leftBound + ((x + 1) * selectionTileSpacing) + (x * selectionTileWidth) and mousePos[0] < leftBound + ((x + 1) * selectionTileSpacing) + (x * selectionTileWidth) + selectionTileWidth and mousePos[1] > selectionPanelHeading + ((y + 1) * selectionTileSpacing) + (y * selectionTileWidth) and mousePos[1] < selectionPanelHeading + ((y + 1) * selectionTileSpacing) + (y * selectionTileWidth) + selectionTileWidth:
                    palette.selected[1] = i
                    palette.selected[2] = selectionInversion[i]

                    # Shift click to invert selection
                    keys = pygame.key.get_mods()
                    if keys & pygame.KMOD_SHIFT:
                        selectionInversion[i] = selectionInversion[i] ^ 1
                        palette.selected[2] = selectionInversion[i]

        # Release
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            mouseHeld = False

    # Process menu actions
    while menuActions:
        action = menuActions.pop(0)
        if action == 'newLevel':
            # Launch new.py in a subprocess
            newLevelScript = os.path.join(scriptDir, 'utility', 'new.py')
            subprocess.Popen([sys.executable, newLevelScript])
        elif action == 'saveLevel':
            level.save('prison') # TODO: Multiple save directories
            print("Level saved to prison.map")
        elif action == 'reloadLevel':
            level.load('prison')
            print("Reloaded prison.map") # TODO: Multiple save directories
        elif isinstance(action, tuple) and action[0] == 'zoom':
            setZoom(action[1])

    # Mouse held down
    if mouseHeld and selectedTileX >= 0 and selectedTileY >= 0:
        placeTile(level, selectedTileX, selectedTileY, 0)

    # Space panning
    if spacePanning and mapWindowRect.collidepoint(mousePos):
        offsetX = pygame.mouse.get_pos()[0] - panningRelativePos[0]
        offsetY = pygame.mouse.get_pos()[1] - panningRelativePos[1]

        scroller.scrollX = panningRelativeScroll[0] + offsetX * (tileSize / relativeTileSize)
        scroller.scrollY = panningRelativeScroll[1] + offsetY * (tileSize / relativeTileSize)
    
    scroller.update()

    screen.fill(BG_COLOR)
    mapWindowSurface.fill((0, 0, 0))

    # Map window
    drawCheckerboard(mapWindowSurface, mapWindowSurface.get_rect())

    # Grid and tiles
    drawMapWindow()

    # Selection Panel
    availablePalettes = palette.paletteData[palette.selected[0]]
    
    for i in range (0, len(availablePalettes)):
        x = (i % 2) + 1
        y = (i + 2) // 2

        inversionShift = 0

        if selectionTileBorder > 1:
            selectionTileBorder /= 3

        selectionRect = pygame.Rect(leftBound + (selectionTileSpacing * x) + (selectionTileWidth * (x - 1)), selectionPanelHeading + (selectionTileSpacing * y) + (selectionTileWidth * (y - 1)), selectionTileWidth, selectionTileWidth)
        pygame.draw.rect(screen, (255, 255, 255), selectionRect)

        previewPoint = XYFromID(selectedTileset, availablePalettes[i][0])

        if selectionInversion[i] == 1:
            inversionShift = 3

        palettePreview = selectedTileset.subsurface(pygame.Rect(previewPoint[0] * tileSize, (previewPoint[1] + inversionShift) * tileSize, 48, 48))

        if i == palette.selected[1]:
            selectionTileBorder *= 3

        screen.blit(pygame.transform.scale(palettePreview, (selectionTileWidth - (2 * selectionTileBorder), selectionTileWidth - (2 * selectionTileBorder))), (leftBound + (selectionTileSpacing * x) + (selectionTileWidth * (x - 1)) + selectionTileBorder, selectionPanelHeading + (selectionTileSpacing * y) + (selectionTileWidth * (y - 1)) + selectionTileBorder))

    # Highlighted tile
    if mapWindowRect.collidepoint(mousePos):
        # Mouse position
        mouseRelX = mousePos[0] - mapWindowRect.x
        mouseRelY = mousePos[1] - mapWindowRect.y

        # Calculate grid offset
        gridOffsetX = (scroller.scrollX % tileSize) * (relativeTileSize / tileSize)
        gridOffsetY = (scroller.scrollY % tileSize) * (relativeTileSize / tileSize)

        # Subtract grid offset before calculating tile position
        adjustedMouseX = mouseRelX - gridOffsetX
        adjustedMouseY = mouseRelY - gridOffsetY

        # Which tile in the viewport (allow negative values for offscreen tiles)
        viewportTileX = int(adjustedMouseX // relativeTileSize)
        viewportTileY = int(adjustedMouseY // relativeTileSize)

        # Thickness
        thickness = 2

        # Calculate rectangle position
        rectX = (viewportTileX * relativeTileSize) + gridOffsetX
        rectY = (viewportTileY * relativeTileSize) + gridOffsetY

        # Draw selection rectangle edges individually, only if they're visible
        # Top edge
        if rectY >= 0 and rectY < mapWindowHeight:
            lineStartX = max(0, rectX)
            lineEndX = min(mapWindowWidth, rectX + relativeTileSize)
            if lineStartX < lineEndX:
                pygame.draw.line(mapWindowSurface, (255, 255, 255), (lineStartX, rectY), (lineEndX, rectY), thickness)

        # Bottom edge
        if rectY + relativeTileSize >= 0 and rectY + relativeTileSize < mapWindowHeight:
            lineStartX = max(0, rectX)
            lineEndX = min(mapWindowWidth, rectX + relativeTileSize)
            if lineStartX < lineEndX:
                pygame.draw.line(mapWindowSurface, (255, 255, 255), (lineStartX, rectY + relativeTileSize), (lineEndX, rectY + relativeTileSize), thickness)

        # Left edge
        if rectX >= 0 and rectX < mapWindowWidth:
            lineStartY = max(0, rectY)
            lineEndY = min(mapWindowHeight, rectY + relativeTileSize)
            if lineStartY < lineEndY:
                pygame.draw.line(mapWindowSurface, (255, 255, 255), (rectX, lineStartY), (rectX, lineEndY), thickness)

        # Right edge
        if rectX + relativeTileSize >= 0 and rectX + relativeTileSize < mapWindowWidth:
            lineStartY = max(0, rectY)
            lineEndY = min(mapWindowHeight, rectY + relativeTileSize)
            if lineStartY < lineEndY:
                pygame.draw.line(mapWindowSurface, (255, 255, 255), (rectX + relativeTileSize, lineStartY), (rectX + relativeTileSize, lineEndY), thickness)

        # Global tile coordinates calculated directly from mouse position and scroll
        selectedTileX = int((scroller.getRealOffsetX() + mouseRelX / relativeTileSize * tileSize) / tileSize)
        selectedTileY = int((scroller.getRealOffsetY() + mouseRelY / relativeTileSize * tileSize) / tileSize)

    elif (selectedTileX > -1) or (selectedTileY > -1):
        selectedTileX = selectedTileY = -1
    
    screen.blit(mapWindowSurface, mapWindowRect.topleft)
    pygame.draw.rect(screen, (255, 255, 255), mapWindowRect, 2)

    # Debug values
    zoomLabel = font.render(f"Zoom: H: {zoomHorizontal}, V: {zoomVertical}, I: {zoomIndex}", True, TEXT_COLOR)
    scrollLabel = font.render(f"Scroll: X: {scroller.getRealOffsetX()}, Y: {scroller.getRealOffsetY()}", True, TEXT_COLOR)
    selectedLabel = font.render(f"Selected: ({selectedTileX}, {selectedTileY}), {level.getTile(1, selectedTileX, selectedTileY)}", True, TEXT_COLOR) # TODO: Make layering

    screen.blit(zoomLabel, (mapWindowWidth + ((screenWidth - mapWindowWidth) / 2) + 4, screenHeight - 40))
    screen.blit(scrollLabel, (mapWindowWidth + ((screenWidth - mapWindowWidth) / 2) + 4, screenHeight - 28))
    screen.blit(selectedLabel, (mapWindowWidth + ((screenWidth - mapWindowWidth) / 2) + 4, screenHeight - 16))

    # Draw windows, handle input
    pygame.display.flip()

    clock.tick(60)

pygame.quit()