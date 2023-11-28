import common
import concurrent
import cupy as cp
import freq_timer
import numpy as np
import os
import pygame
import random
import threading
import time
import timer_pool
import traceback

FPS = 30
TPS = 10

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

Y_SPEED = SCREEN_HEIGHT / 32
X_SPEED = Y_SPEED * common.PHI

MAP_SIZE = 128

CELL_SIZE = 5

RANDOM_FLIP_CHANCE = 0.01
# RANDOM_FLIP_CHANCE = 1
# RANDOM_FLIP_CHANCE = 0

class Runtime:

    def __init__(self, **kargs):
        self.thread_pool = concurrent.futures.ThreadPoolExecutor(min(32, os.cpu_count()+4))
        self.lock = threading.Condition()

        self.running = None
        self.timer_pool = timer_pool.TimerPool()

        self.gol_np = np.zeros((MAP_SIZE,MAP_SIZE), dtype=np.uint8)
        self.last_gol_np = self.gol_np
        # self.gol_np = np.random.randint(0,2,(MAP_SIZE,MAP_SIZE), dtype=np.uint8)
        # self.x_offset = 0
        # self.y_offset = 0
        self.last_gol_t = None

        self.map_surface = pygame.Surface((MAP_SIZE*CELL_SIZE,MAP_SIZE*CELL_SIZE))
        self.map_surface.fill((255,255,255))

        self.gol_run_exit_done = False
        self.run_exit_done = False

    def run(self):
        try:
            pygame.init()

            self.screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT),flags=0)
            pygame.display.set_caption('Conway\'s Game of Life')

            self.last_gol_t = time.time()
            self.thread_pool.submit(self.gol_run)

            t0 = time.time()
            self.timer_pool.add_timer(freq_timer.FreqTimer(self, t0, FPS, lambda sec: self.screen_tick(sec)))
            self.timer_pool.add_timer(freq_timer.FreqTimer(self, t0+1/2/FPS, FPS, lambda sec: self.event_tick(sec)))

            self.timer_pool.run()

            self.run_exit_done = True
        except:
            self.run_exit_done = True
            raise
        finally:
            self.run_exit_done = True

    def gol_run(self):
        try:
            my_gol_cp = cp.random.randint(0,2,(MAP_SIZE,MAP_SIZE), dtype=cp.uint8)
            t = time.time()
            # my_gol_cp = cp.zeros((MAP_SIZE,MAP_SIZE), dtype=cp.uint8)
            # my_gol_cp[49,50] = 1
            # my_gol_cp[50,49] = 1
            # my_gol_cp[50,50] = 1
            # my_gol_cp[50,51] = 1
            # my_gol_cp[51,51] = 1
            while self.is_continue():
                my_gol_cp0 = cp.zeros((MAP_SIZE+2,MAP_SIZE+2), dtype=cp.uint8)
                my_gol_cp0[1:-1,1:-1] = my_gol_cp
                my_gol_cp0[0,1:-1] = my_gol_cp[-1,:]
                my_gol_cp0[-1,1:-1] = my_gol_cp[0,:]
                my_gol_cp0[1:-1,0] = my_gol_cp[:,-1]
                my_gol_cp0[1:-1,-1] = my_gol_cp[:,0]
                my_gol_cp0[0,0] = my_gol_cp[-1,-1]
                my_gol_cp0[0,-1] = my_gol_cp[-1,0]
                my_gol_cp0[-1,0] = my_gol_cp[0,-1]
                my_gol_cp0[-1,-1] = my_gol_cp[0,0]
                my_gol_cp1 = cp.zeros((MAP_SIZE,MAP_SIZE), dtype=cp.uint8)
                # my_gol_cp1[:,:] = my_gol_cp
                for i in range(-1,2):
                    for j in range(-1,2):
                        if i==0 and j==0: continue
                        my_gol_cp1 += my_gol_cp0[1+i:MAP_SIZE+1+i,1+j:MAP_SIZE+1+j]
                my_gol_cp1 *= 2
                my_gol_cp1 += my_gol_cp
                my_gol_cp5 =  my_gol_cp1 >= 5
                my_gol_cp7 =  my_gol_cp1 <= 7
                my_gol_cp = my_gol_cp5 * my_gol_cp7

                if random.random() < RANDOM_FLIP_CHANCE:
                    hori = random.randint(0,1)
                    i = random.randint(0,MAP_SIZE-1)
                    if hori == 0:
                        my_gol_cp[(i+0)%MAP_SIZE,:] = cp.random.randint(0,2,MAP_SIZE, dtype=cp.uint8)
                        # my_gol_cp[(i+1)%MAP_SIZE,:] = cp.random.randint(0,2,MAP_SIZE, dtype=cp.uint8)
                        # my_gol_cp[(i+2)%MAP_SIZE,:] = cp.random.randint(0,2,MAP_SIZE, dtype=cp.uint8)
                    else:
                        my_gol_cp[:,(i+0)%MAP_SIZE] = cp.random.randint(0,2,MAP_SIZE, dtype=cp.uint8)
                        # my_gol_cp[:,(i+1)%MAP_SIZE] = cp.random.randint(0,2,MAP_SIZE, dtype=cp.uint8)
                        # my_gol_cp[:,(i+2)%MAP_SIZE] = cp.random.randint(0,2,MAP_SIZE, dtype=cp.uint8)

                with self.lock:
                    self.gol_np = cp.asnumpy(my_gol_cp)
                
                self.last_gol_t = time.time()

                tdiff = max(0,t + 1/TPS - t)
                time.sleep(tdiff)
                t += tdiff
        except:
            traceback.print_exc()
        self.gol_run_exit_done = True


    def screen_tick(self, sec):
        # self.screen.fill((255,255,255))

        if not self.is_continue():
            self.timer_pool.stop()
            return

        with self.lock:
            my_gol_np = self.gol_np

        # x_offset_int = int(self.x_offset)
        # y_offset_int = int(self.y_offset)
        # print(f'x_offset_int={x_offset_int}, y_offset_int={y_offset_int}')
        color0 = (255,255,255)
        color1 = (0,0,0)

        if (my_gol_np != self.last_gol_np).any():
            for y in range(MAP_SIZE):
                for x in range(MAP_SIZE):
                    # if my_gol_np[y,x] == 0: continue
                    # # color = (255,255,255)
                    # # if x == 0: color = (255,0,0)
                    # # if y == 0: color = (0,255,0)
                    # # if my_gol_np[y,x] == 1: color = (0,0,0)
                    # xx_start = ((x*CELL_SIZE + x_offset_int + CELL_SIZE)%(CELL_SIZE*MAP_SIZE))-CELL_SIZE
                    # yy_start = ((y*CELL_SIZE + y_offset_int + CELL_SIZE)%(CELL_SIZE*MAP_SIZE))-CELL_SIZE
                    # xx = xx_start
                    # while True:
                    #     if xx >= SCREEN_WIDTH: break
                    #     yy = yy_start
                    #     while True:
                    #         if yy >= SCREEN_HEIGHT: break
                    #         pygame.draw.rect(self.screen, color, (xx,yy,CELL_SIZE,CELL_SIZE))
                    #         yy += CELL_SIZE*MAP_SIZE
                    #     xx += CELL_SIZE*MAP_SIZE
                    if my_gol_np[y,x] == self.last_gol_np[y,x]: continue
                    color = color0 if my_gol_np[y,x] == 0 else color1
                    self.map_surface.fill(color=color, rect=(x*CELL_SIZE,y*CELL_SIZE,CELL_SIZE,CELL_SIZE))
        self.last_gol_np = my_gol_np

        x_offset_int = int(sec*X_SPEED%(CELL_SIZE*MAP_SIZE))
        if x_offset_int > 0: x_offset_int-=CELL_SIZE*MAP_SIZE
        y_offset_int = int(sec*Y_SPEED%(CELL_SIZE*MAP_SIZE))
        if y_offset_int > 0: y_offset_int-=CELL_SIZE*MAP_SIZE

        for xx in range(x_offset_int, SCREEN_WIDTH, CELL_SIZE*MAP_SIZE):
            for yy in range(y_offset_int, SCREEN_HEIGHT, CELL_SIZE*MAP_SIZE):
                self.screen.blit(self.map_surface, (xx,yy))

        # for xx in range(x_offset_int, SCREEN_WIDTH, CELL_SIZE*MAP_SIZE):
        #     self.screen.fill(color=(255,0,0), rect=(xx,0,1,SCREEN_HEIGHT))

        # for yy in range(y_offset_int, SCREEN_HEIGHT, CELL_SIZE*MAP_SIZE):
        #     self.screen.fill(color=(0,255,0), rect=(0,yy,SCREEN_WIDTH,1))

        # self.x_offset += X_SPEED * sec
        # self.y_offset += Y_SPEED * sec
        # self.x_offset %= SCREEN_WIDTH
        # self.y_offset %= SCREEN_HEIGHT

        pygame.display.flip()

    def event_tick(self, sec):
        if not self.is_continue():
            self.timer_pool.stop()
            return
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.timer_pool.stop()

    def is_continue(self):
        try:
            if self.gol_run_exit_done: return False
            if self.run_exit_done: return False
            if time.time() - self.last_gol_t > 60: return False
        except:
            return False
        return True

instance = None

def run(**kargs):
    global instance
    instance = Runtime(**kargs)
    instance.run()
