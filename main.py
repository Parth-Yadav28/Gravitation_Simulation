import random
import math

import pygame

pygame.init()

#Constants
WIDTH = 1366
HEIGHT = 705
SCREEN_SIZE = (WIDTH,HEIGHT)
G = 0.0001 #6.67 * (10 ** (-11))
MIN_DISTANCE = 5
STAR_NO = 100
FPS = 60
dt = 1/FPS

WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
BLACK = (0,0,0)

#Density related colours
DENSITY_WHITE = (255,255,255)
DENSITY_GREEN = (0,255,0)

#Display
disp = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption('Gravitation Simulation')

#integration method
verlet_integration_and_not_euler_integration = True #true for verlet and false for euler

#Functions
def distance(body1,body2):
    return math.sqrt((body1.x - body2.x) ** 2 + (body1.y - body2.y) ** 2)

def force(body1, body2):
    d = max(distance(body1, body2), MIN_DISTANCE)  #Prevents extreme forces
    return (G * body1.mass * body2.mass) / (d ** 2)

#Classes
class Body:
    FPS = 60
    dt = 1/ FPS
    def __init__(self,x,y,mass,radius,color,x_vel = 0,y_vel = 0):
        self.x = x
        self.y = y
        self.mass = mass
        self.radius = radius
        self.x_vel = x_vel
        self.y_vel = y_vel
        self.color = color

        #Previous position for Verlet integration
        self.prev_x = self.x - self.x_vel * dt
        self.prev_y = self.y - self.y_vel * dt

    def update(self):
        total_x_acc, total_y_acc = 0, 0

        for body in perm_bodies:
            if body != self:
                d = distance(self, body)  # Prevent division by near-zero

                if d > MIN_DISTANCE:
                    f = force(self, body)

                    angle = math.atan2(body.y - self.y, body.x - self.x)

                    total_x_acc += (f * math.cos(angle)) / self.mass
                    total_y_acc += (f * math.sin(angle)) / self.mass

        if verlet_integration_and_not_euler_integration:
            #Verlet Integration
            new_x = 2 * self.x - self.prev_x + total_x_acc * dt ** 2
            new_y = 2 * self.y - self.prev_y + total_y_acc * dt ** 2

            self.prev_x, self.prev_y = self.x, self.y  #Store old position
            self.x, self.y = new_x, new_y  #Update to new position

        elif not verlet_integration_and_not_euler_integration:
            #Eulers Integration
            self.x_vel += total_x_acc * dt
            self.y_vel += total_y_acc * dt

            self.x += self.x_vel * dt
            self.y += self.y_vel * dt

    def draw(self):
        pygame.draw.circle(disp,self.color,(int(self.x),int(self.y)),self.radius)

#Bodies On Screen
perm_bodies = []
temp_body_pos = None
temp_radius = 0
temp_phase = 0

#Main
def main():
    running = True
    clock = pygame.time.Clock()
    global temp_body_pos,temp_radius,temp_phase,perm_bodies,DENSITY_GREEN,DENSITY_WHITE

    #For Stars
    random_x,random_y = [],[]
    for i in range(STAR_NO):
        random_no_one = random.randint(1, WIDTH)
        random_x.append(random_no_one)
        random_no_two = random.randint(1, HEIGHT)
        random_y.append(random_no_two)

    #Game Loop
    while running:
        clock.tick(FPS)
        DENSITY_WHITE = (DENSITY_GREEN[1], DENSITY_GREEN[1], DENSITY_GREEN[1])

        # Scale DENSITY_GREEN[1] from 10 (500 kg/m³) to 255 (150,000 kg/m³)
        density = 500 + (((265 - DENSITY_GREEN[1]) - 10) / (255 - 10)) * (150000 - 500)

        mouse_pos = pygame.mouse.get_pos()

        #Handle Event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                if event.key == pygame.K_BACKSPACE:
                    perm_bodies = []

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Right-click
                if temp_phase == 0:
                    temp_body_pos = mouse_pos
                    temp_phase = 1  # Move to next phase

                elif temp_phase == 1:
                    temp_radius = int(math.dist(temp_body_pos, mouse_pos))
                    temp_phase = 2  # Move to next phase

                elif temp_phase == 2:
                    DENSITY_GREEN = (0,max(min(int(math.dist(temp_body_pos,mouse_pos))*2,255),10),0)
                    temp_phase = 3

                elif temp_phase == 3:
                    line_length = int(math.dist(temp_body_pos, mouse_pos))
                    angle = math.atan2(mouse_pos[1] - temp_body_pos[1], mouse_pos[0] - temp_body_pos[0])

                    # Realistic mass formula (mass = density * volume of sphere)
                    mass = (4 / 3) * math.pi * (temp_radius ** 3) * density

                    x_vel = -(int(line_length * math.cos(angle) / 1.5))  #Scale velocity
                    y_vel = -(int(line_length * math.sin(angle) / 1.5))

                    perm_bodies.append(Body(temp_body_pos[0],temp_body_pos[1],mass if mass != 0 else 1,temp_radius,DENSITY_WHITE,x_vel,y_vel))
                    temp_phase = 0  #Reset for next object

        #Update Game Loop
        for body in perm_bodies:
            body.update()

        #Draw On Screen
        disp.fill(BLACK)  #Clear the screen

        for i in range(STAR_NO): #Draw background of stars
            pygame.draw.circle(disp, WHITE, (random_x[i],random_y[i]), 1)

        if temp_phase == 1 and temp_body_pos:
            pygame.draw.circle(disp,GREEN,temp_body_pos,int(math.dist(temp_body_pos, mouse_pos)))

        elif temp_phase == 2 and temp_body_pos:
            pygame.draw.circle(disp,(0,max(min(int(math.dist(temp_body_pos,mouse_pos))*2,255),10),0),temp_body_pos,temp_radius)

        elif temp_phase == 3 and temp_body_pos:
            pygame.draw.circle(disp,DENSITY_GREEN,temp_body_pos,temp_radius)
            pygame.draw.line(disp,DENSITY_GREEN,temp_body_pos,mouse_pos,3)

        for body in perm_bodies:
            body.draw()

        pygame.display.update()  # Refresh the display

    pygame.quit()#Quit :(


if __name__ == "__main__":
    main()