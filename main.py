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

class Boid:
    def __init__(self, startx, starty, radius):
        self.x = startx
        self.y = starty
        self.direction = 0.0
        self.speed = 1
        self.radius = radius

    def update(self, boids):
        self.direction += (random.randrange(-2, 3) * 180) / math.pi

        for boid in boids:
            dist = math.sqrt((boid.x - self.x)*(boid.x - self.x) + (boid.y - self.y)*(boid.y - self.y))
            if (dist < 10):
                self.direction += (self.direction - boid.direction) / 2

        self.x += self.speed * math.cos(self.direction)
        self.y += self.speed * math.sin(self.direction)

        if self.x < 0:
            self.x = SCREEN_WIDTH
        if self.x > SCREEN_WIDTH:
            self.x = 0
        if self.y < 0:
            self.y = SCREEN_HEIGHT
        if self.y > SCREEN_HEIGHT:
            self.y = 0

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

    print len(world.boids)

    random.seed(time.time())
    while (True):
        for event in pygame.event.get():
            if (event.type == QUIT) or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

        world.update()
        world.draw()

        WINDOWSURFACE.blit(world.surface, (0,0))

        print FPSCLOCK.get_fps()
        pygame.display.flip()
        FPSCLOCK.tick(FPS)

if __name__ == '__main__':
    main()
