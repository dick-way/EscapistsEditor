import pygame
import math

class SmoothScroller:
    def __init__(self, scrollXMax, scrollYMax):

        self.scrollX = scrollXMax
        self.scrollY = scrollYMax
        self.scrollXMax = scrollXMax
        self.scrollYMax = scrollYMax
        self.velocityX = 0
        self.velocityY = 0
        self.friction = 0.90
        self.sensitivity = 0.8 # Scroll speed

    def setScrollBounds(self, scrollXMax, scrollYMax):

        self.scrollXMax = scrollXMax
        self.scrollYMax = scrollYMax

        # Update bounds
        self.scrollX = max(0, min(self.scrollX, scrollXMax))
        self.scrollY = max(0, min(self.scrollY, scrollYMax))

    def handleScroll(self, dx, dy):

        # Add to velocity instead of directly to position
        self.velocityX += dx * self.sensitivity
        self.velocityY += dy * self.sensitivity

    def update(self):

        # Apply velocity to position
        newScrollX = self.scrollX + self.velocityX
        newScrollY = self.scrollY + self.velocityY
        
        self.scrollX = int(newScrollX) if self.velocityX > 0 else math.ceil(newScrollX)
        self.scrollY = int(newScrollY) if self.velocityY > 0 else math.ceil(newScrollY)

        # Keep in bounds
        if self.scrollX < 0:
            self.scrollX = 0
            self.velocityX = 0

        elif self.scrollX > self.scrollXMax:
            self.scrollX = self.scrollXMax
            self.velocityX = 0

        if self.scrollY < 0:
            self.scrollY = 0
            self.velocityY = 0

        elif self.scrollY > self.scrollYMax:
            self.scrollY = self.scrollYMax
            self.velocityY = 0

        # Apply friction (momentum decay)
        self.velocityX *= self.friction
        self.velocityY *= self.friction

    def getRealOffsetX(self):
        return int(self.scrollXMax - self.scrollX)

    def getRealOffsetY(self):
        return int(self.scrollYMax - self.scrollY)