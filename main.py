#!/usr/bin/env python
import pygame
from pygame.locals import *
import sys
import random
import time
import math

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
CAMERA_WIDTH = SCREEN_WIDTH
CAMERA_HEIGHT = SCREEN_HEIGHT
FPS = 60
MAX_OBJECTS = 50
MAX_LEVELS = 8
SEP_WEIGHT = 0.005
SEP_DIST = 30
ALI_DIST = 30
COH_DIST = 30

class Boid:
    def __init__(self, startx, starty, radius):
        #Based on angle = 0 and speed = 1...
        self.xVector = 1

        self.yVector = 0
        self.x = startx
        self.y = starty
        self.direction = 0
        self.speed = 1
        self.radius = radius

    def update(self, boidList):
        #self.direction += random.randrange(-2, 3)
        #Make list of close boids.
        sepBoids = []
        aliBoids = []
        cohBoids = []

        for boid in boidList:
            dist = self.distance(boid.x, self.x, boid.y, self.y)
            if dist < SEP_DIST:
                sepBoids.append(boid)
            if dist < ALI_DIST:
                aliBoids.append(boid)
            if dist < COH_DIST:
                cohBoids.append(boid)

        xSep, ySep = self.separation(sepBoids)

        self.xVector += xSep
        self.yVector += ySep
        self.direction = math.atan(self.yVector / self.xVector)
        self.speed = math.sqrt(self.xVector * self.xVector + self.yVector * self.yVector)
        # Position.
        self.x += self.xVector
        self.y += self.yVector

        if self.x < 0:
            self.x = SCREEN_WIDTH
        if self.x > SCREEN_WIDTH:
            self.x = 0
        if self.y < 0:
            self.y = SCREEN_HEIGHT
        if self.y > SCREEN_HEIGHT:
            self.y = 0

    '''
    Given a list of boids, it will return the vector for the separation.
    '''
    def separation(self, boidList):
        xVector = 0
        yVector = 0

        # Vector addition the vectors of our boidList
        for boid in boidList:
            xVector += boid.xVector
            yVector += boid.yVector

        # Return direction of new vector.
        return (-xVector * SEP_WEIGHT, -yVector * SEP_WEIGHT)

    def distance(self, x1, x2, y1, y2):
        return math.sqrt(abs(x1 - x2) * abs(x1 - x2) + abs(y1 - y2) * abs(y1 - y2))

    def draw(self, surface):
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x), int(self.y)), self.radius, 1)

class QuadTree():
    def __init__(self, width, height, x, y, level):
        self.objects = []
        self.x = x
        self.y = y
        self.w = width
        self.h = height
        self.level = level
        self.nodes = []

    def clear(self):
        self.objects = []
        for node in self.nodes:
            node.clear()

    def split(self):
        x = self.x
        y = self.y
        w = self.w / 2
        h = self.h / 2
        self.nodes.append(QuadTree(x, y, w, h, self.level + 1))
        self.nodes.append(QuadTree(x + w, y, w, h, self.level + 1))
        self.nodes.append(QuadTree(x, y + h, w, h, self.level + 1))
        self.nodes.append(QuadTree(x + w, y + h, w, h, self.level + 1))

    def getIndex(self, x, y):
        verticalMidpoint = self.x + (self.w / 2)
        horizontalMidpoint = self.y + (self.h / 2)

        topQuad = y < horizontalMidpoint
        botQuad = y > horizontalMidpoint
        leftQuad = x < verticalMidpoint
        rightQuad = x > verticalMidpoint

        index = -1
        if (topQuad and rightQuad):
            index = 0
        elif (topQuad and leftQuad):
            index = 1
        elif (botQuad and leftQuad):
            index = 2
        elif (botQuad and rightQuad):
            index = 3

        return index

    def insert(self, boid):
        if (self.nodes != []):
            index = self.getIndex(boid.x, boid.y)
            if (index != -1):
                self.nodes[index].insert(boid)
                return

        objects.append(boid)
        if (len(object) > MAX_OBJECTS and self.level < MAX_LEVELS):
            if (self.nodes == []):
                split()

            i = 0
            while (i < len(objects)):
                index = self.getIndex(objects[i].x, objects[i].y)
                if (index != -1):
                    self.nodes[index].insert(objects.pop(i))
                else:
                    i += 1

    def retrieve(self, boids, x, y):
        index = self.getIndex(x,y)
        if (index != -1 and self.nodes != []):
            self.nodes[index].retrieve(boids, x, y)

        boids += self.objects
        return boids

class World:
    def __init__(self, surface, width, height):
        self.surface = surface
        self.w = width
        self.h = height
        self.boids = []
        self.tree = QuadTree(self.w, self.h, 0, 0, 0)

    def update(self):
        for boid in self.boids:
            neighbors = self.tree.retrieve([], boid.x, boid.y)
            boid.update(neighbors)

    def draw(self):
        self.surface.fill((0,0,0))
        for boid in self.boids:
            boid.draw(self.surface)

def main():
    pygame.init()
    FPSCLOCK = pygame.time.Clock()

    WINDOWSURFACE = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    GAMESURFACE = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Boids")

    world = World(GAMESURFACE, SCREEN_WIDTH, SCREEN_HEIGHT)

    for x in range(0, 1280, 12):
        for y in range(0, 720, 12):
            world.boids.append(Boid(x,y,1))

    print(len(world.boids))

    random.seed(time.time())
    while (True):
        for event in pygame.event.get():
            if (event.type == QUIT) or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

        world.update()
        world.draw()

        WINDOWSURFACE.blit(world.surface, (0,0))

        print(FPSCLOCK.get_fps())
        pygame.display.flip()
        FPSCLOCK.tick(FPS)

if __name__ == '__main__':
    main()
