#!/usr/bin/env python3
import pygame
import random
from random import shuffle, randint as rng
import copy
import math
import csv

pygame.init() 

#Pic dump
playersprite = pygame.image.load('pics/spiderman.png')
portalsprite = pygame.image.load('pics/portal.png')
enemy1leftsprite = pygame.image.load('pics/enemy1left.png') #100,50 flying
enemy1rightsprite = pygame.image.load('pics/enemy1right.png') #100,50 flying
enemy2leftsprite = pygame.image.load('pics/enemy4left.png') #50,50 flying
enemy2rightsprite = pygame.image.load('pics/enemy4right.png') #50,50 flying
enemy3sprite = pygame.image.load('pics/enemy3.png') #75,50 walking
enemy4sprite = pygame.image.load('pics/enemy2.png') #100,50 flying
coinsprite=pygame.image.load('pics/coin.png')

#exitsprite = pygame.image.load('exit.png')
homebackground = pygame.image.load('pics/background.jpg')

screenwidth, screenheight = 1150,600
mapwidth,mapheight = 3000,700
background = pygame.Surface((mapwidth, mapheight))
background.fill((230,180,100))
mapsurface = pygame.Surface((mapwidth,mapheight))

playerwidth, playerheight = 50,75
time = 0
timecounter = 0


clock=pygame.time.Clock()
window = pygame.display.set_mode((screenwidth,screenheight))
pygame.display.set_caption('2D Game')
font = pygame.font.SysFont('Comic Sans MS',20,False,False)

shutdown = False
gravity = 1 #acceleration

#Pygame functions:
def clicker():
    global shutdown
    mousepos = (0,0)
    clickedpos = (0,0)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            shutdown =  True
        if event.type == pygame.MOUSEBUTTONDOWN:
            mousepos= pygame.mouse.get_pos()
    return mousepos

def inbutton(click,buttonpos):
    value=False
    try:
        if click[0] in range(buttonpos[0],buttonpos[0]+buttonpos[2]):
            if click[1] in range(buttonpos[1],buttonpos[1]+buttonpos[3]):
                value=True
    except:
        pass
    return value

def overlap(pos1,pos2):
    #pos = x,y,width,height
    left  = max(pos1[0], pos2[0])
    top   = max(pos1[1], pos2[1])
    right = min(pos1[0]+pos1[2], pos2[0]+pos2[2])
    bot   = min(pos1[1]+pos1[3], pos2[1]+pos2[3])
    if right-left > 0 and bot-top > 0:
        area = (left-right) * (top-bot)
    else:
        area = 0
    return area

body_list=list()
wall_list = list()
boundary_list=list()
movingwall_list=list()
player_list = list()
enemy_list = list()
projectile_list = list()
item_list = list()
coin_list=[]
portal_list=list()

listlist = [body_list, wall_list, boundary_list, movingwall_list, player_list, enemy_list, projectile_list, item_list, portal_list]

class Body(pygame.sprite.Sprite):
    def __init__(self, x=0, y=0, width=1, height=1, 
                 xvel=0, yvel=0,
                 image=pygame.Surface((1,1))):
        super().__init__()
        self.x=x
        self.y=y
        self.width=width
        self.height=height
        self.xvel=xvel
        self.yvel=yvel
        self.image=image
        self.pos=(self.x, self.y, self.width, self.height)
        self.hitbox = (self.x, self.y, self.width, self.height)
        body_list.append(self)
        self.offset = (0,0)

    def draw(self,win=window):
        win.blit(self.image,self.pos,(0,0,self.pos[2],self.pos[3]))
    def movement(self):
        pass

#Player
class Shadow(Body):
    def __init__(self,x=0, y=0, width=playerwidth, height=playerheight, 
                 xvel=0, yvel=0,
                 image=pygame.Surface((playerwidth,playerheight))):
        super().__init__(x,y,width,height,xvel,yvel,image)
        self.shadowcounter=0
        self.image.fill((255,255,255))
        self.image.set_colorkey((255,255,255))
        pygame.draw.rect(self.image, (0,0,0), (self.x,self.y,self.width,self.height),3)
    
    
        
class Player(Body):
    def __init__(self, 
                 x=1, y=0, width=playerwidth, height=playerheight, 
                 xvel=5, yvel=0,flyvel=15,
                 image=pygame.Surface((playerwidth,playerheight)), health= 5,
                 up=pygame.K_w,
                 down=pygame.K_s,
                 left=pygame.K_a,
                 right=pygame.K_d,
                 one=pygame.K_1, two=pygame.K_2, three=pygame.K_3, four=pygame.K_4,
                 previous=pygame.K_q, next=pygame.K_e,
                 ):
        super().__init__(x,y,width,height,xvel,yvel,image) #inherited
        self.up, self.down, self.left, self.right = up, down, left, right #passed in
        self.one,self.two,self.three,self.four,self.previous,self.next=one,two,three,four,previous,next #Items
        self.previouscounter, self.nextcounter = 0, 0
        self.hitbox = (self.x, self.y, self.width, self.height) #To be set (after pics are added)
        self.health=health
        self.currentslot=1
        #movement variables
        self.jumping=False
        self.jump2=False
        self.standing=True
        self.impact=True
        self.facing=1
        self.flying=False
        self.flyvel = flyvel
        self.shadowcounter=0
        self.shadow=Shadow()
        self.shadowdict=dict()
        for n in range(120):
            self.shadowdict[n]=(self.x,self.y,self.width,self.height)

        #mechanics variables
        self.stealth = True
        self.stealthcounter = 0
        self.invul = False
        self.invulcounter = 0
        self.portals= False
        self.timewarp = False
        self.rocket=False
        self.hooking = False
        self.hook=None
        self.wallcling=False
        self.inventory=list()
        self.rewindpos=(self.x,self.y,self.width,self.height)
        self.coin=0

        #game settings
        player_list.append(self)

    def update_pos(self):
        offset_x = min(max(self.x+self.width//2-screenwidth//2, 0) , mapwidth-screenwidth)
        offset_y = min(max(self.y-screenheight//2, 0), mapheight - screenheight)
        self.offset = (offset_x,offset_y)
        self.hitbox = (self.x, self.y, self.width, self.height)
        self.pos =    (self.x, self.y, self.width, self.height)
        self.shadowcounter= (self.shadowcounter+1)%120
        self.shadowdict[self.shadowcounter] = (self.x,self.y,self.width,self.height)
        self.rewindpos = self.shadowdict[(self.shadowcounter+1)%120]
        self.shadow.pos = self.shadowdict[(self.shadowcounter+1)%120]

    def collision(self,direction):
        collide = False
        temp_x = self.x + direction
        temp_hitbox = temp_x, self.y, self.width, self.height
        for wall in wall_list:
            if overlap(wall.pos,temp_hitbox) > 0:
                collide = True
        for boundary in boundary_list:
            if overlap(boundary.pos,temp_hitbox)>0:
                collide=True
        return collide


    def touchdown(self,direction):
        landed=False
        headbang=False
        temp_y = self.y + direction #1 in the direction
        temp_hitbox = self.x,temp_y,self.width,self.height
        if self.yvel<0: #going up
            for wall in wall_list:
                if overlap(wall.pos,temp_hitbox)>0:
                    if wall.pos[1]+wall.pos[3] > temp_y:
                        headbang = True
        else:
            for wall in wall_list:
                if overlap(wall.pos,temp_hitbox) > 0:
                    if wall.pos[1]<temp_y+self.height:
                        landed = True

        if self.yvel<0: #going up
            for boundary in boundary_list:
                if overlap(boundary.pos,temp_hitbox)>0:
                    if boundary.pos[1]+boundary.pos[3] > temp_y:
                        headbang = True
        else:
            for boundary in boundary_list:
                if overlap(boundary.pos,temp_hitbox) > 0:
                    if boundary.pos[1]<temp_y+self.height:
                        landed = True
        return landed,headbang



    def fly(self):
        opposite = self.endpos[1] - self.startpos[1]
        adjacent = self.endpos[0] - self.startpos[0]
        adjacent = 1 if adjacent==0 else adjacent
        opposite = 1 if opposite==0 else opposite
        theta = math.atan(opposite/adjacent)
        #x_direction = int(adjacent/abs(adjacent))
        #y_direction = int(opposite/abs(opposite))
        x_direction = 1 if self.endpos[0]> self.startpos[0] else -1
        y_direction =  1 if self.endpos[1]> self.startpos[1] else -1
        self.x_speed = abs(round(self.flyvel*math.cos(theta)))
        self.y_speed = abs(round(self.flyvel*math.sin(theta)))
        if self.wallcling==False:
            for _ in range(self.x_speed):
                impact=self.collision(x_direction)
                if not impact:
                    self.x+=x_direction
                else:
                    self.wallcling=True
                    self.flying=False
            for _ in range(self.y_speed):
                impact = self.touchdown(y_direction)
                if not (impact[0] or impact[1]):
                    self.y+=y_direction
                else:
                    self.flying=False
        if self.flying==False:
            if self.hook in body_list:
                body_list.remove(self.hook)
            self.hooking=False
            
    
    def movement(self): 
        global shutdown, exiting,counter,ded
        mousepos=(0,0)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                shutdown = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                mousepos= pygame.mouse.get_pos()
        if inbutton(mousepos, escape.pos):
            exiting=True
            counter-=1
            ded=True
        keys = pygame.key.get_pressed()
        if self.flying: #Cannot move
            self.jumping,self.jump2=False,False
            self.fly()
        else: #not flying, can move
            for _ in range(int(self.xvel)):
                if keys[self.left] and keys[self.right]:
                    pass
                elif keys[self.left]:
                    self.facing=-1
                    if not self.collision(-1):
                        self.x-=1
                        if self.wallcling:
                            self.yvel=-10
                            self.jumping=True
                            self.jump2=True
                        self.wallcling=False
                elif keys[self.right]:
                    self.facing=1
                    if not self.collision(1):
                        self.x+=1
                        if self.wallcling:
                            self.jumping=True
                            self.jump2=True
                            self.yvel=-10
                        self.wallcling=False
            if self.wallcling:
                if self.collision(1) or self.collision(-1):
                    pass
                else:
                    self.wallcling=False
            if self.jumping==False: #walking
                if not self.touchdown(1)[0]: #in midair
                    if self.wallcling:
                        if keys[self.up]: #jump off from clinging position
                            self.jumping=True
                            self.jump2=True
                            self.yvel=-10
                            self.wallcling=False
                        else: #clinging on to wall
                            if not self.touchdown(1)[0]: #not landing
                                self.y+=gravity
                    else: #walk off platform
                        self.yvel=0
                        self.jumping=True
                elif keys[self.up]:
                    self.jumping=True
                    self.yvel=-15
                else: #continue walking
                    pass
            else: #is in midjump
                if self.yvel<=0: #going up
                    #for i in range(abs(self.yvel)):
                    if not self.touchdown(self.yvel)[1]: #not headbang
                        self.y+=self.yvel #-=gravity
                    else:
                        for i in range(self.yvel,0):
                            if self.touchdown(i)[1]:
                                pass 
                            else:
                                self.y+=i
                                break
                        self.yvel*=-1
                    if self.jump2==False and self.yvel>-5:
                        if keys[self.up]:
                            self.yvel=-10
                            self.jumping=True
                            self.jump2=True
                else: #going down
                    self.yvel = min(self.yvel,15)
                    if keys[self.up] and self.jump2==False:
                        self.yvel=-10
                        self.jumping=True
                        self.jump2=True
                    elif not self.touchdown(self.yvel)[0]: #not landing
                        self.y+=self.yvel #gravity
                    else:
                        for i in range(self.yvel,0,-1):
                            if self.touchdown(i)[0]:
                                pass 
                            else:
                                self.y+=i
                                break
                        self.yvel = - gravity #because += gravity at the end
                        self.jumping=False
                        self.jump2=False
                            #break
                self.yvel+=gravity
            #Clicks
            if mousepos!=(0,0):
                if pygame.mouse.get_pressed()[0] and self.hooking==False: #Left click
                    if self.wallcling==False:
                        offset_x, offset_y = self.offset
                        new_mousepos = (mousepos[0]+offset_x,mousepos[1]+offset_y)
                        self.hook = Hook(clickpos = new_mousepos, x = self.x+self.width//2, y = self.y+self.height//3)
                        self.hooking=True
        #Items
        if mousepos!=(0,0):
            if pygame.mouse.get_pressed()[2]: # Right click
                offset_x, offset_y = self.offset
                new_mousepos = (mousepos[0]+offset_x,mousepos[1]+offset_y)
                if self.useitem(new_mousepos):
                    self.stealth=False
                else:
                    print('no item here')
            if pygame.mouse.get_pressed()[0] and self.flying: #Left click
                self.hooking=False
                self.flying=False
                if self.hook in body_list:
                    body_list.remove(self.hook)
                self.yvel=0
                self.jumping=True
                self.jump2=False
                

        if self.previouscounter:
            self.previouscounter+=1
            if self.previouscounter>15:
                self.previouscounter=0
        if self.nextcounter:
            self.nextcounter+=1
            if self.nextcounter>15:
                self.nextcounter=0
        if keys[self.previous]:
            if self.previouscounter==0:
                self.currentslot-=1
                if self.currentslot<1:
                    self.currentslot=4
            self.previouscounter+=1
        if keys[self.next]:
            if self.nextcounter==0:
                self.currentslot+=1
                if self.currentslot>4:
                    self.currentslot=1
            self.nextcounter+=1
        if keys[self.one]:
            self.currentslot=1
        if keys[self.two]:
            self.currentslot=2
        if keys[self.three]:
            self.currentslot=3
        if keys[self.four]:
            self.currentslot=4  
   
        #Enemy encounter
        templist=list()
        for enemy in enemy_list:
            kill = False
            temp_y = self.hitbox[1] + self.hitbox[3] - 20
            temp_hitbox = self.hitbox[0], temp_y, self.hitbox[2], 20
            temp_enemy = enemy.hitbox[0], enemy.hitbox[1], enemy.hitbox[2], 1
            if overlap(temp_enemy,temp_hitbox) > 0 and self.yvel - enemy.yvel>-1:
                self.yvel=-15
                self.jumping=True
                self.jump2=True
                self.stealth=False
                templist.append(enemy)
            elif self.invul:
                pass
            elif overlap(enemy.hitbox,self.hitbox) > 0:
                self.health -=1
                self.invul=True
                self.stealth = False
                self.invulcounter=0
            else: #No interaction
                pass
        for enemy in templist:
            if enemy in enemy_list:
                enemy_list.remove(enemy)
            if enemy in body_list:
                body_list.remove(enemy)

        #Item encounter
        for item in item_list:
            if overlap(item.hitbox,self.hitbox) > 0:
                item.addplayer()
            else: #No interaction
                pass
        #Portal encounter
        teleport=False
        for portal in portal_list:
            if overlap(portal.pos, self.hitbox)>0 and portal.used==False:
                teleport=True
                portal.used=True
                print('overlapping')
        if teleport:
            print('teleporting')
            for portal in portal_list:
                if portal.used:
                    pass
                else:
                    portal.used=True
                    self.x,self.y,self.width,self.height = portal.x,portal.y,portal.width,portal.height

        #Mechanics            
        if self.invul:
            self.invulcounter+=1
            if self.invulcounter>60:
                self.invulcounter=0
                self.invul=False
                       
        if self.stealth==False:
            self.stealthcounter+=1
            if self.stealthcounter>150: #5s
                if self.invul:
                    pass
                else:
                    self.stealthcounter=0
                    self.stealth=True
        if self.hook in body_list:   
            self.hooking=True
        else:
            self.hooking=False
        self.update_pos()

    def useitem(self,mousepos=None):
        item=None
        for obj in self.inventory:
           if self.currentslot == obj.slot:
               item=obj
               break
        if item:
            item.effect(mousepos)
            if item in self.inventory:
                self.inventory.remove(item)
            return True
        else:
            return False
        
    def unstealth(self):
        self.stealthcounter=0
        self.stealth=False
    def damage(self, n=1):
       
        if n>0 and self.invul==False:
            self.unstealth()
            self.health-=n
            self.invul=True
            self.invulcounter=0

    def draw(self,win=window):
        self.image.fill((0,100,0))
        self.image.set_colorkey((0,100,0))
        transparency=100
        if self.stealth:
            transparency=50
        if self.facing == 1:
            self.image.blit(playersprite,(0,0))
        else: #self.facing == -1
            self.image.blit(playersprite,(0,0))
        if self.invul:
            self.image.fill((255,255,255,transparency))
            text = font.render(str(round(2-self.invulcounter/30, 2) ),1,(0,0,0))
            self.image.blit(text,(10,30))
        if self.stealth:
            text = font.render('ninja',1,(255,255,255))
            self.image.blit(text,(0,30))
        win.blit(self.image,self.pos)
        



#Wall

class Boundary(Body):
    def __init__(self,  x=1, y=1, width=1, height=1, xvel=0, yvel=0,image=pygame.Surface((screenwidth,screenheight))):
        super().__init__(x,y,width,height,xvel,yvel,image)
        self.image.fill((255,255,50))
        boundary_list.append(self)




class Wall(Body):
    def __init__(self,  x=1, y=1, width=1, height=1, xvel=5, yvel=0,image=pygame.Surface((screenwidth,screenheight))):
        super().__init__(x,y,width,height,xvel,yvel,image)
        self.image.fill((177,100,50))
        wall_list.append(self)
        

    def collision(self):            
        temp_x = self.x + self.facing
        temp_hitbox = temp_x, self.y, self.width, self.height
        enemyhit,playerhit = False, False
        for enemy in enemy_list:
            if overlap(enemy.hitbox,temp_hitbox) > 0:
                enemyhit = True
        for player in player_list:
            if overlap(player.hitbox,temp_hitbox) >0:
                playerhit=True


        
                


class Movingwall(Wall):
    def __init__(self,  x=1, y=1, width=1, height=1, xvel=5, yvel=0,image=pygame.Surface((screenwidth,screenheight)),maxdisplacement=100,facing=1):
        super().__init__(x,y,width,height,xvel,yvel,image)
        self.image.fill((139,0,139))
        self.facing=facing
        self.displacement=0
        self.z=False
        self.maxdisplacement=maxdisplacement
        movingwall_list.append(self)

    def movement(self):
        temp_x = self.x + self.facing
        temp_hitbox = temp_x, self.y, self.width, self.height
        enemyhit,playerhit = False, False
        for enemy in enemy_list:
            if overlap(enemy.hitbox,temp_hitbox) > 0:
                enemyhit = True
        for player in player_list:
            if overlap(player.hitbox,temp_hitbox) >0:
                playerhit=True
        for _ in range(self.xvel):
            if self.displacement<self.maxdisplacement and self.z==False:
                self.x+=1
                self.displacement+=1
                
                if playerhit:
                    if player.x>self.x:
                        player.x+=2
                    else: player.x-=2                   
            else:
                self.facing*=-1
                self.x-=1
                self.displacement-=1
                
                if playerhit:
                    if player.x<self.x:
                        player.x-=2
                    else:
                        player.x+=2
                if self.displacement==0:
                    self.facing*=-1
                    self.z=False
            if self.displacement==self.maxdisplacement:
                self.z=True
                
                    
        self.pos=(self.x,self.y,self.width,self.height)
        self.hitbox=self.pos

# Vertical movement

class Movingwallv(Wall):
    def __init__(self,  x=1, y=1, width=1, height=1, xvel=5, yvel=0,image=pygame.Surface((screenwidth,screenheight)),maxdisplacement=100,facing=1):
        super().__init__(x,y,width,height,xvel,yvel,image)
        self.image.fill((139,0,139))
        self.facing=facing
        self.displacement=0
        self.z=False
        self.maxdisplacement=maxdisplacement
        movingwall_list.append(self)

    def movement(self):
        temp_y = self.y + self.facing
        temp_hitbox = self.x, temp_y, self.width, self.height
        enemyhit,playerhit = False, False
        for enemy in enemy_list:
            if overlap(enemy.hitbox,temp_hitbox) > 0:
                enemyhit = True
        for player in player_list:
            if overlap(player.hitbox,temp_hitbox) >0:
                playerhit=True
        for _ in range(self.xvel):
            if self.displacement<self.maxdisplacement and self.z==False:
                self.y+=1
                self.displacement+=1
                
                if playerhit:
                    if player.y>self.y:
                        player.y+=2
                    else: player.x-=2                   
            else:
                self.facing*=-1
                self.y-=1
                self.displacement-=1                
                if playerhit:
                    if player.y<self.y:
                        player.y-=2
                    else:
                        player.y+=2
                if self.displacement==0:
                    self.facing*=-1
                    self.z=False
            if self.displacement==self.maxdisplacement:
                self.z=True
                
                    
        self.pos=(self.x,self.y,self.width,self.height)
        self.hitbox=self.pos

class Bulletwall(Wall):
    def __init__(self,  x=1, y=1, width=1, height=1, xvel=5, yvel=0,image=pygame.Surface((screenwidth,screenheight)),angle=0):
        super().__init__(x,y,width,height,xvel,yvel,image)
        self.image.fill((220,100,100))
        self.angle=angle
        self.counter=rng(0,30)


    def movement(self):
        if self.counter==1: 
            Icicles(x=self.x+7, y=self.y+7, width=10, height=10, xvel=0, yvel=0,image=pygame.Surface((10,10)),slot=0, flyvel=15,angle=self.angle)
        else:
            if self.counter>79:
                self.counter=0
        self.counter+=1
        
            
     





#Enemy
class Enemy(Body):
    def __init__(self, x=rng(1,500), y=rng(1,100), width=playerwidth, height=playerheight, xvel=3, yvel=5,image=pygame.Surface((playerwidth,playerheight)),health=1,
                    ):
        super().__init__(x,y,width,height,xvel,yvel,image)
        self.image.fill((100,50,50))
        self.facing=rng(0,1)*2-1
        self.hitbox = (self.x, self.y, self.width, self.height)
        self.jumping=False
        self.health=health
        enemy_list.append(self)

    def collision(self,direction):
        collide = False
        temp_x = self.x + direction
        temp_hitbox = temp_x, self.y, self.width, self.height
        for wall in wall_list:
            if overlap(wall.pos,temp_hitbox) > 0:
                collide = True
        for wall in boundary_list:
            if overlap(wall.pos,temp_hitbox) > 0:
                collide = True
        return collide

    def touchdown(self,direction=1):
        landed=False
        headbang=False
        temp_y = self.y + direction #1 in the direction
        temp_hitbox = self.x,temp_y,self.width,self.height
        if self.yvel<0: #going up
            for wall in wall_list:
                if overlap(wall.pos,temp_hitbox)>0:
                    if wall.pos[1]+wall.pos[3] > temp_y:
                        headbang = True
            for wall in boundary_list:
                if overlap(wall.pos,temp_hitbox)>0:
                    if wall.pos[1]+wall.pos[3] > temp_y:
                        headbang = True
        else:
            for wall in wall_list:
                if overlap(wall.pos,temp_hitbox) > 0:
                    if wall.pos[1]<temp_y+self.height:
                        landed = True
            for wall in boundary_list:
                if overlap(wall.pos,temp_hitbox) > 0:
                    if wall.pos[1]<temp_y+self.height:
                        landed = True
        return landed,headbang

    def movement(self):
        if self.health<=0:
            if self in enemy_list:
                enemy_list.remove(self)
                return
        if player_list[0].stealth == True: #(doesnt recognise player)
            for _ in range(self.xvel):
                if self.collision(self.facing):
                    self.facing*=-1
                    break
                else:
                    self.x+=self.facing
            if self.jumping==False: #walking
                if not self.touchdown(1)[0]: #walk off platform
                    self.yvel=0
                    self.jumping=True
                elif not rng(0,15):
                    self.jumping=True
                    self.yvel=-15
                else: #continue walking
                    pass
            else: #is self.jumping
                if self.yvel<0: #going up
                    for i in range(abs(self.yvel)):
                        if not self.touchdown(-1)[1]: #not headbang
                            self.y-=gravity
                        else:
                            self.yvel*=-gravity
                            break
                else: #going down
                    for i in range(self.yvel):
                        if not self.touchdown(1)[0]: #not landing
                            self.y+=gravity
                        else:
                            self.yvel = - gravity #because += gravity at the end
                            self.jumping=False        
                            break
                self.yvel+=gravity

        else:
            if self.x > player_list[0].pos[0]:
                self.facing=-1
            elif self.x < player_list[0].pos[0]:
                self.facing=1
            for _ in range(self.xvel):
                if self.collision(self.facing):
                    self.facing*=-1
                    break
                else:
                    self.x+=self.facing
            if self.jumping==False: #walking
                if not self.touchdown(1)[0]: #walk off platform
                    self.yvel=0
                    self.jumping=True
                elif not rng(0,15):
                    self.jumping=True
                    self.yvel=-15
                else: #continue walking
                    pass
            else: #is self.jumping
                if self.yvel<0: #going up
                    for i in range(abs(self.yvel)):
                        if not self.touchdown(-1)[1]: #not headbang
                            self.y-=gravity
                        else:
                            self.yvel*=-gravity
                            break
                else: #going down
                    for i in range(self.yvel):
                        if not self.touchdown(1)[0]: #not landing
                            self.y+=gravity
                        else:
                            self.yvel = - gravity #because += gravity at the end
                            self.jumping=False        
                            break
                self.yvel+=gravity


        self.pos=self.x,self.y,self.width,self.height
        self.hitbox=self.pos
                
            
    

    def draw(self,win=window):
        if self.facing == 1:
            self.image.fill((100,50,50))
            win.blit(self.image,self.pos)
        else: #self.facing == -1
            self.image.fill((50,50,100))
            win.blit(self.image,self.pos)

class Enemy1(Enemy):
    def __init__(self, x=rng(1,500), y=rng(1,100), width=100, height=50, xvel=3, yvel=5,image=pygame.Surface((100,50)),health=1,
):
        super().__init__(x, y, width, height, xvel, yvel,image,health)

    def draw(self,win=window):
        self.image.fill((0,255,0))
        self.image.set_colorkey((0,255,0))
        if self.facing == 1:
            self.image.blit(enemy1rightsprite, (0,0))
            win.blit(self.image,self.pos)
        else: #self.facing == -1
            self.image.blit(enemy1leftsprite, (0,0))
            win.blit(self.image,self.pos)


class Enemy2u(Enemy):
    def __init__(self, x=rng(1,500), y=rng(1,100), width=50, height=50, xvel=3, yvel=5,image=pygame.Surface((50,50)),health=1,maxdisplacement=100
):
        super().__init__(x, y, width, height, xvel, yvel,image,health)
        self.displacement=0
        self.maxdisplacement=maxdisplacement
        self.z=False          
    
    def movement(self):
        if self.health<=0:
            if self in enemy_list:
                enemy_list.remove(self)
                return               
        if self.displacement<self.maxdisplacement and self.z==False:
            self.y-=2
            self.displacement+=1              
        else:
            self.y+=2
            self.displacement-=1
            if self.displacement==0:
                self.z=False
        if self.displacement==self.maxdisplacement:
            self.z=True
        self.pos=(self.x,self.y,self.width,self.height)
        self.hitbox=self.pos
    
    def draw(self,win=window):
        self.image.fill((0,255,0))
        self.image.set_colorkey((0,255,0))
        if self.facing == 1:
            self.image.blit(enemy2rightsprite, (0,0))
            win.blit(self.image,self.pos)
        else: #self.facing == -1
            self.image.blit(enemy2leftsprite, (0,0))
            win.blit(self.image,self.pos)

class Enemy2d(Enemy):
    def __init__(self, x=rng(1,500), y=rng(1,100), width=50, height=50, xvel=3, yvel=5,image=pygame.Surface((50,50)),health=1,maxdisplacement=100
):
        super().__init__(x, y, width, height, xvel, yvel,image,health)
        self.displacement=100
        self.maxdisplacement=maxdisplacement
        self.z=False
           
    def movement(self):
        if self.health<=0:
            if self in enemy_list:
                enemy_list.remove(self)
                return
                
        if self.displacement<self.maxdisplacement and self.z==False:
            self.y-=2
            self.displacement+=1              
        else:
            self.y+=2
            self.displacement-=1
            if self.displacement==0:
                self.z=False
        if self.displacement==self.maxdisplacement:
            self.z=True
                
                    
        self.pos=(self.x,self.y,self.width,self.height)
        self.hitbox=self.pos
    

    def draw(self,win=window):
        self.image.fill((0,255,0))
        self.image.set_colorkey((0,255,0))
        if self.facing == 1:
            self.image.blit(enemy2rightsprite, (0,0))
            win.blit(self.image,self.pos)
        else: #self.facing == -1
            self.image.blit(enemy2leftsprite, (0,0))
            win.blit(self.image,self.pos)

class Enemy3l(Enemy):
    def __init__(self, x=rng(1,500), y=rng(1,100), width=75, height=50, xvel=3, yvel=5,image=pygame.Surface((75,50)),health=1,maxdisplacement=100
):
        super().__init__(x, y, width, height, xvel, yvel,image,health)
        self.displacement=0
        self.maxdisplacement=maxdisplacement
        self.z=False          
    
    def movement(self):
        if self.health<=0:
            if self in enemy_list:
                enemy_list.remove(self)
                return               
        if self.displacement<self.maxdisplacement and self.z==False:
            self.x-=2
            self.displacement+=1              
        else:
            self.x+=2
            self.displacement-=1
            if self.displacement==0:
                self.z=False
        if self.displacement==self.maxdisplacement:
            self.z=True
        self.pos=(self.x,self.y,self.width,self.height)
        self.hitbox=self.pos
    
    def draw(self,win=window):
        self.image.fill((0,255,0))
        self.image.set_colorkey((0,255,0))
        self.image.blit(enemy3sprite, (0,0))
        win.blit(self.image,self.pos)


class Enemy3r(Enemy):
    def __init__(self, x=rng(1,500), y=rng(1,100), width=75, height=50, xvel=3, yvel=5,image=pygame.Surface((75,50)),health=1,maxdisplacement=100
):
        super().__init__(x, y, width, height, xvel, yvel,image,health)
        self.displacement=100
        self.maxdisplacement=maxdisplacement
        self.z=False
           
    def movement(self):
        if self.health<=0:
            if self in enemy_list:
                enemy_list.remove(self)
                return
                
        if self.displacement<self.maxdisplacement and self.z==False:
            self.x-=2
            self.displacement+=1              
        else:
            self.x+=2
            self.displacement-=1
            if self.displacement==0:
                self.z=False
        if self.displacement==self.maxdisplacement:
            self.z=True
                                   
        self.pos=(self.x,self.y,self.width,self.height)
        self.hitbox=self.pos
    

    def draw(self,win=window):
        self.image.fill((0,255,0))
        self.image.set_colorkey((0,255,0))
        self.image.blit(enemy3sprite, (0,0))
        win.blit(self.image,self.pos)
#Projectile
class Projectile(Body):
    def __init__(self, clickpos, x=1, y=1, width=3, height=3, xvel=15, yvel=0,image=pygame.Surface((3,3)),reach=450,hooky=0,hookx=0):
        super().__init__(x,y,width,height,xvel,yvel,image)
        self.hitbox = (self.x, self.y, self.width, self.height)
        self.clickpos=clickpos #fixed
        self.startpos=(self.x,self.y) #fixed
        self.vel=xvel #for now
        self.dist=0 #fixed
        opposite = (self.clickpos[1]-self.startpos[1])
        adjacent = (self.clickpos[0]-self.startpos[0])
        adjacent = 1 if adjacent==0 else adjacent
        theta = math.atan(opposite/adjacent)
        if adjacent<0:
            theta+=math.pi
        self.theta=theta
        self.alive=True
        self.reach=reach
        self.hookx = round(self.vel*math.cos(self.theta))
        self.hooky = round(self.vel*math.sin(self.theta))
        projectile_list.append(self)

    def descent(self):
        pass

    def collision(self):     
        pass

    def movement(self):
        if self.alive:
            self.dist += self.vel
            self.descent()
            if self.dist >= self.reach:
                self.alive = False
                if self in body_list:
                    body_list.remove(self)
            self.x,self.y=self.pos[0]+self.hookx,self.pos[1]+self.hooky
            self.pos = (self.x,self.y,self.width,self.height)
            self.hitbox=self.pos
            self.collision()

    def draw(self,win=window):
        self.image.fill((0,0,0))
        win.blit(self.image,self.pos)        
    


class Hook(Projectile):
    def __init__(self, clickpos, x=1, y=1, width=3, height=3, xvel=25, yvel=0,image=pygame.Surface((3,3)),reach=400,hooky=0,hookx=0):
        super().__init__(clickpos,x,y,width,height,xvel,yvel,image,reach,hooky,hookx)
        self.hitbox = (self.x-4, self.y-4, self.width+7, self.height+7)

    def movement(self):
        pass
    
    def movement2(self):
        if self.alive:
            self.dist += self.vel
            self.descent()
            if self.dist >= self.reach:
                self.alive = False
                if self in body_list:
                    body_list.remove(self)
            self.x,self.y=self.pos[0]+self.hookx,self.pos[1]+self.hooky
            self.pos = (self.x,self.y,self.width,self.height)
            self.hitbox=self.pos
            self.collision()

    def collision(self):
        wallhit,objecthit = False, False
        for wall in wall_list:
            if overlap(wall.pos,self.hitbox) > 0:
                wallhit = True
        for boundary in boundary_list:
            if overlap(boundary.pos,self.hitbox) > 0:
                objecthit = True
        for enemy in enemy_list:
            if overlap(enemy.hitbox,self.hitbox) > 0:
                objecthit = True
        for item in item_list:
            if overlap(item.hitbox,self.hitbox) >0:
                item.flying=True
                objecthit=True
        if wallhit:
            self.alive=False
            player_list[0].flying=True
            player_list[0].startpos = player_list[0].x+player_list[0].width//2, player_list[0].y+player_list[0].height//3
            player_list[0].endpos = self.x,self.y
        elif objecthit:
            self.alive=False
            if self in body_list:
                body_list.remove(self)        
        return (wallhit,objecthit)

    def descent(self):
        if self.dist >= self.reach//2:          
            self.hooky += self.yvel
            self.yvel+=1 if self.yvel<1 else 0

    def draw(self,win=window):
        self.image.fill((0,0,0))
        win.blit(self.image,self.pos)
        if player_list[0].hooking==True:
            pygame.draw.line(win,(255,255,255),(self.pos[0],self.pos[1]),(player_list[0].x+player_list[0].width//2,player_list[0].y + player_list[0].height//3),2)

class Portal(Projectile):
    def __init__(self, clickpos, x=1, y=1, width=playerwidth, height=playerheight, xvel=15, yvel=0,image=pygame.Surface((playerwidth,playerheight)),reach=800,hooky=0,hookx=0):
        super().__init__(clickpos,x,y,width,height,xvel,yvel,image,reach,hooky,hookx)
        self.hitbox = (self.x, self.y, self.width, self.height)
        self.clickpos=(self.clickpos[0]+playerwidth//2, self.clickpos[1]+playerheight//2)
        self.startpos=(self.startpos[0]-playerwidth//2, self.startpos[1]-playerheight//3)
        portal_list.append(self)
        self.used = True
        self.usedcounter = 0
        
    def movement(self):
        if self.alive:
            self.dist += self.vel
            self.descent()
            if self.dist >= self.reach:
                self.alive = False
                if self in body_list:
                    body_list.remove(self)
            self.x,self.y=self.pos[0]+self.hookx,self.pos[1]+self.hooky
            self.pos = (self.x,self.y,self.width,self.height)
            self.hitbox=self.pos
            self.collision()
        if self.used:
           self.usedcounter+=1
        if self.usedcounter>30:
           self.usedcounter=0
           self.used=False

    def collision(self):
        wallhit=False
        for wall in wall_list:
            if overlap(wall.pos,self.hitbox) > 0:
                wallhit = True
        for wall in boundary_list:
            if overlap(wall.pos,self.hitbox) > 0:
                wallhit = True
        if wallhit:
            self.alive=False
            self.x-=self.hookx
            self.y-=self.hooky
            self.pos=self.x,self.y,self.width,self.height
            self.used=False
            self.hitbox=self.pos

    def draw(self,win=window):
        self.image.fill((0,100,0))
        self.image.set_colorkey((0,100,0))
        self.image.blit(portalsprite,(0,0))
        win.blit(self.image,self.pos)      

class Rocket(Projectile):
    def __init__(self, clickpos, x=30, y=30, width=30, height=30, xvel=15, yvel=0,image=pygame.Surface((30,30)),reach=500,hooky=0,hookx=0):
        super().__init__(clickpos,x,y,width,height,xvel,yvel,image,reach,hooky,hookx)
        self.hitbox = (self.x, self.y, self.width, self.height)

    def collision(self):
        explosionpos=self.x-150,self.y-150,300,300
        objecthit = False
        for wall in wall_list:
            if overlap(wall.pos,self.hitbox) > 0:
                objecthit = True
        for enemy in enemy_list:
            if overlap(enemy.hitbox,self.hitbox) > 0:
                objecthit = True
        for item in item_list:
            if overlap(item.hitbox,self.hitbox) >0:    
                objecthit=True
        for boundary in boundary_list:
            if overlap(boundary.hitbox,self.hitbox) >0:    
                objecthit=True
        for portal in portal_list:
            if overlap(portal.hitbox,self.hitbox) >0:
                objecthit=True
        if objecthit:
            templist=list()
            self.alive=False
            for wall in wall_list:
                if overlap(wall.pos,explosionpos) > 0:
                    templist.append(wall)
            for enemy in enemy_list:
                if overlap(enemy.pos,explosionpos) > 0:
                    templist.append(enemy)
            for item in item_list:  
                if overlap(item.pos,explosionpos) > 0:
                    templist.append(item)
            for portal in portal_list:  
                if overlap(portal.pos,explosionpos) > 0:
                    templist.append(portal)
            if self in body_list:
                body_list.remove(self)
            for obj in templist:
                if obj in body_list:
                    body_list.remove(obj)
                if obj in item_list:
                    item_list.remove(obj)
                if obj in wall_list:
                    wall_list.remove(obj)
                if obj in enemy_list:
                    enemy_list.remove(obj)
                if obj in portal_list:
                    portal_list.remove(obj)
#Items
class Item(Body):
    def __init__(self, x=200, y=200, width=30, height=30, xvel=0, yvel=0,image=pygame.Surface((30,30)),slot=0, flyvel=15):
        super().__init__(x,y,width,height,xvel,yvel,image)
        self.hitbox = (self.x, self.y, self.width, self.height)
        self.slot=slot
        self.flyvel=flyvel
        self.flying=False
        item_list.append(self)

    def addplayer(self):
        itemcount=0
        for item in player_list[0].inventory:
            if item.slot==self.slot:
                itemcount+=1
        if itemcount<3:
            player_list[0].inventory.append(self)
        else:
            print('too many of this item')
        if self in item_list:
            item_list.remove(self)
        if self in body_list:
            body_list.remove(self)
        

    def fly(self):
        endpos = player_list[0].x+player_list[0].width//2,player_list[0].y+player_list[0].height//3,player_list[0]
        adjacent = endpos[0] - self.x
        opposite = endpos[1] - self.y
        (adjacent,opposite)
        denom = (adjacent**2 + opposite**2)**0.5
        denom = denom if denom else 1
        L = self.flyvel / denom
        self.x += round(adjacent * L)
        self.y += round(opposite * L)
        self.pos = (self.x,self.y,self.width,self.height)
        self.hitbox = self.pos

    def movement(self):
        if self.flying:
            self.fly()

    def collision(self):     
        playerhit = False
        for player in player_list:
            if overlap(player.hitbox,self.hitbox) > 0:
                playerhit = True
        return playerhit

class Invul(Item):
    def __init__(self, x=200, y=200, width=30, height=30, xvel=0, yvel=0,image=pygame.Surface((30,30)),slot=1, flyvel=15,timer=5):
        super().__init__( x, y, width, height, xvel, yvel,image,slot, flyvel)
        self.image.fill((100,100,100))
        self.hitbox = (self.x, self.y, self.width, self.height)
        self.timer = timer

    def effect(self,mousepos=None):
        player_list[0].invul = True
        player_list[0].invulcounter = 0

class Portalpp(Item):
    def __init__(self, x=300, y=200, width=30, height=30, xvel=0, yvel=0,image=pygame.Surface((30,30)),slot=2 , flyvel=15,timer=5, ):
        super().__init__( x, y, width, height, xvel, yvel,image,slot,flyvel)
        self.hitbox = (self.x, self.y, self.width, self.height)
        self.timer = timer

    def addplayer(self):
        itemcount=0
        for item in player_list[0].inventory:
            if item.slot==self.slot:
                itemcount+=1
        if itemcount<6:
            player_list[0].inventory.append(self)
            itemcount+=1
            if itemcount<6:
                player_list[0].inventory.append(Portalpp())
        else:
            print('Too many portals. Maximum 6.')
        if self in item_list:
            item_list.remove(self)
        if self in body_list:
            body_list.remove(self)

    def effect(self,mousepos=None):
        Portal(mousepos,player_list[0].x,player_list[0].y)
        while len(portal_list)>2:
            old_portal = portal_list.pop(0)
            if old_portal in body_list:
                body_list.remove(old_portal)

class Timewarp(Item):
    def __init__(self, x=400, y=200, width=30, height=30, xvel=0, yvel=0,image=pygame.Surface((30,30)), slot=3, flyvel=15,timer=5, ):
        super().__init__(x, y, width, height, xvel, yvel,image,slot, flyvel)
        self.image.fill((177,177,0))
        self.hitbox = (self.x, self.y, self.width, self.height)
        self.timer = timer

    def effect(self,mousepos=None):
        player_list[0].x,player_list[0].y,player_list[0].width,player_list[0].height=player_list[0].rewindpos       

class Rocketpp(Item):
    def __init__(self, x=500, y=200, width=30, height=30, xvel=0, yvel=0,image=pygame.Surface((30,30)),slot=4, flyvel=15,timer=5, ):
        super().__init__(x, y, width, height, xvel, yvel,image,slot, flyvel)
        self.hitbox = (self.x, self.y, self.width, self.height)
        self.timer = timer
        self.image.fill((255,0,0))

    def effect(self,mousepos=None):
        Rocket(mousepos,player_list[0].x,player_list[0].y)




class Heart(Item):
    def __init__(self,x=1, y=1, width=25, height=25, xvel=0, yvel=0,image=pygame.Surface((25,25)),slot=0, flyvel=15,timer=5, ):
        super().__init__(x, y, width, height, xvel, yvel,image,slot, flyvel)
        self.hitbox = (self.x, self.y, self.width, self.height)
        self.timer = timer
    def addplayer(self):
        self.effect()
        if self in item_list:
            item_list.remove(self)
        if self in body_list:
            body_list.remove(self)
    def effect(self,mousepos=None):
        player_list[0].health += 1 #if player_list[0].health<5 else 0      

class Coin(Item):
    def __init__(self,x=1, y=1, width=25, height=25, xvel=0, yvel=0,image=coinsprite,slot=0, flyvel=15,timer=5, ):
        super().__init__(x, y, width, height, xvel, yvel,image,slot, flyvel)
        self.hitbox = (self.x, self.y, self.width, self.height)
        self.timer = timer
        coin_list.append(self)
    def addplayer(self):
        self.effect()
        if self in item_list:
            item_list.remove(self)
        if self in body_list:
            body_list.remove(self)
    def effect(self,mousepos=None):
        player_list[0].coin+=1   

class Icicles(Item):
    def __init__(self,x=1, y=1, width=25, height=25, xvel=0, yvel=0,image=pygame.Surface((25,25)),slot=0, flyvel=15,angle=0, ):
        super().__init__(x, y, width, height, xvel, yvel,image,slot, flyvel)
        self.hitbox = (self.x, self.y, self.width, self.height)
        self.angle = angle # if angle<=math.pi else angle+math.pi
        self.dist=0

    def addplayer(self):
        self.effect()
        if self in item_list:
            item_list.remove(self)
        if self in body_list:
            body_list.remove(self)

    def effect(self,mousepos=None):
        player_list[0].damage(1) 



    def movement(self):
        movex = round(self.flyvel*math.cos(self.angle))
        movey = round(self.flyvel*math.sin(self.angle))
        self.x+=movex
        self.y+=movey 
        self.dist+=self.flyvel
        if self.dist>350:
            if self in item_list:
                item_list.remove(self)
            if self in body_list:
                body_list.remove(self)
        if self.dist>50:
            for wall in wall_list:
                if overlap(self.hitbox, wall.hitbox):
                    if self in item_list:
                        item_list.remove(self)
                    if self in body_list:
                        body_list.remove(self)
            for wall in boundary_list:
                if overlap(self.hitbox, wall.hitbox):
                    if self in item_list:
                        item_list.remove(self)
                    if self in body_list:
                        body_list.remove(self)
        self.pos=self.x,self.y,self.width,self.height
        self.hitbox=self.pos
      
                
        
        
        
    
class Firewall(Item):
    def __init__(self,x=600, y=400, width=100, height=100, xvel=0, yvel=0,image=pygame.Surface((screenwidth,screenheight)), slot=0,flyvel=0):
        Wall(x,y,width,height)
        x-=1
        y-=1
        width+=2
        height+=2
        super().__init__(x, y, width, height, xvel, yvel,image,slot, flyvel)
        self.image.fill((220,20,60))
        self.hitbox=self.x,self.y,self.width,self.height

    def addplayer(self):
        playerhit = False
        for player in player_list:
            if overlap(player.hitbox,self.hitbox) >0:
                playerhit=True            
        if playerhit and player_list[0].invul==False:
            player_list[0].health -=1
            player_list[0].invul=True
            player_list[0].stealth = False
            player_list[0].invulcounter=0 
        else: #No interaction
            pass

    def fly(self):
        pass
    def movement(self):
        pass



#Exit Portal
exiting=False
complete=True
class Exit(Body):
    def __init__(self,x=0, y=0, width=playerwidth, height=playerheight, 
                 xvel=0, yvel=0,
                 image=pygame.Surface((playerwidth,playerheight))):
        super().__init__(x,y,width,height,xvel,yvel,image)
        self.image.fill((255,255,255))
        self.image.set_colorkey((255,255,255))
    def draw(self,win=window):
        self.image.fill((255,255,255))
        self.image.set_colorkey((255,255,255))
        pygame.draw.rect(self.image,(0,0,0),(0,0,30,30))
        #self.image.blit(exitsprite,(0,0))
        win.blit(self.image,self.pos)
    def movement(self):
        global exiting
        for player in player_list:
            if overlap(player.pos, self.pos) and complete==True:
                exiting=True

    



#Creating objs


enemycd,itemcd=0,0
def createobj():
    return
    global enemycd,itemcd
    enemies = len(enemy_list)
    if enemies < 2:
        if enemycd>120:
            Enemy1()
            enemycd=0
        else:
            enemycd+=1
    items = len(item_list)
    if items<4:
        if itemcd>60:
            itemcd=0
            Invul()
            Portalpp()
            Timewarp()
            Rocketpp()
        else:
            itemcd+=1
#Map making
cellwidth, cellheight = 25,25

def mapmaker(map_list):
    i=0
    for row in map_list:
        for j, obj in enumerate(row):
            pos = (j*cellwidth,i*cellheight)
            objmaker(obj,pos)
        i+=1

def objmaker(obj,position):
    x,y=position
    if obj:
        if obj=='w': 
            Wall(x,y,cellwidth,cellheight)
        elif obj=='mr' or obj=='ml':
            Movingwall(x,y,cellwidth,cellheight,)
        elif obj=='mu' or obj=='md':
            Movingwallv(x,y,cellwidth,cellheight,)
        elif obj=='md':
            pass
        elif obj=='b': 
            Boundary(x,y,cellwidth,cellheight)
        elif obj=='f':
            Firewall(x,y,cellwidth,cellheight)
        elif obj=='invul':
            Invul(x,y,cellwidth,cellheight)
        elif obj=='portal':
            Portalpp(x,y,cellwidth,cellheight)
        elif obj=='time':
            Timewarp(x,y,cellwidth,cellheight)
        elif obj=='r':
            Rocketpp(x,y,cellwidth,cellheight)
        elif obj=='h':
            Heart(x,y,cellwidth,cellheight)
        elif obj=='c':
            Coin(x,y)
        elif obj=='p':
            Player(x,y)
        elif obj=='ex':
            Exit(x,y,cellwidth,cellheight)
        elif obj=='e1':
            Enemy1(x,y)
        elif obj=='e2d':
            Enemy2d(x,y)
        elif obj=='e2u':
            Enemy2u(x,y)
        elif obj=='e3r':
            Enemy3r(x,y)
        elif obj=='e3l':
            Enemy3l(x,y)
        elif '_' in obj:
            obj=obj.split('_')
            if obj[0]=='bw':
                Bulletwall(x,y,cellwidth,cellheight,angle=float(obj[1]))
                
            
def openmap(filename):
    global newmap,background,mapsurface
    global mapwidth,mapheight
    newmap = None
    with open(filename,mode='r') as csv_file:
        mapheight=0
        mapwidth=0
        for line in csv.reader(csv_file):
            mapwidth = len(line)*cellwidth
            mapheight+=cellheight

        background = pygame.Surface((mapwidth, mapheight))
        background.fill((230,180,100))
        mapsurface = pygame.Surface((mapwidth,mapheight))

        csv_file.seek(0)
        mapmaker(csv.reader(csv_file))

    #Screen limit
        Boundary(-1,-100,1,mapheight+100) #Left bounds
        Boundary(mapwidth,-100,1,mapheight+100) #Right bounds
        Boundary(0,-100,mapwidth,1) #Top bounds
        Boundary(0,mapheight,mapwidth,1) #Bottom bounds
    


def blititems():
    one,two,three,four=0,0,0,0
    items = player_list[0].inventory
    for item in items:
        if item.slot==1:
            one+=1
        if item.slot==2:
            two+=1
        if item.slot==3:
            three+=1
        if item.slot==4:
            four+=1
    pygame.draw.rect(window, (255,255,255), (250,screenheight-30,30,30))
    text=font.render(str(one),1,(0,0,0))
    window.blit(text,(250,screenheight-30,30,30))
    pygame.draw.rect(window, (255,255,255), (290,screenheight-30,30,30))
    text=font.render(str(two),1,(0,0,0))
    window.blit(text,(290,screenheight-30,30,30))
    pygame.draw.rect(window, (255,255,255), (330,screenheight-30,30,30))
    text=font.render(str(three),1,(0,0,0))
    window.blit(text,(330,screenheight-30,30,30))
    pygame.draw.rect(window, (255,255,255), (370,screenheight-30,30,30))
    text=font.render(str(four),1,(0,0,0))
    window.blit(text,(370,screenheight-30,30,30))
    selected = player_list[0].currentslot
    pygame.draw.rect(window, (0,255,0,), (210+selected*40,screenheight-30,30,30),3)


def refresh():
    global time,timecounter
    newx,newy = player_list[0].offset
    blit_rect = newx, newy, screenwidth, screenheight
    render_rect = newx-50, newy-50, screenwidth+100, screenheight+100
    mapsurface.blit(background,(0,0))
    for body in body_list:
        if overlap(body.pos,render_rect):
            body.draw(mapsurface)
            body.movement()
    for player in player_list:
        if player.hook:
            player.hook.movement2()
    timecounter +=1
    if timecounter == 30:
        time +=1
        timecounter =0
    window.blit(mapsurface,(0,0),blit_rect)
    text=font.render(str(player_list[0].health),1,(0,0,0))
    window.blit(text,(screenwidth-100,10))
    text=font.render('Coins ' + str(player_list[0].coin),1,(0,0,0))
    window.blit(text,(screenwidth-200,10))    
    text=font.render('Time ' + str(time),1,(0,0,0))
    window.blit(text,(screenwidth-300,10))

    escape.draw()

    blititems()
    pygame.display.update()


#Blit windows





buttonwidth,buttonheight = 120,40
class Button():
    def __init__(self,text='Button',pos=(screenwidth,screenheight,buttonwidth,buttonheight),play=lambda:True):
        self.pos = pos
        self.text = text
        text = font.render(str(text),1,(0,0,0))
        self.art = pygame.Surface((self.pos[2],self.pos[3]))
        self.play=play
    def draw(self):
        self.art.fill((215,220,235))
        text = font.render(str(self.text),1,(0,0,0))
        width = text.get_width()
        self.art.blit(text,(self.pos[2]//2-width//2-2,5))
        window.blit(self.art,self.pos)


startgame=Button(text='Play',pos=(0,0,buttonwidth,buttonheight))
howtoplay=Button('How To Play')
back=Button('< Back',pos=(10,10,buttonwidth,buttonheight))
tutorial=Button('Tutorial',pos=(screenwidth-buttonwidth-10,10,buttonwidth,buttonheight))
escape = Button('Restart', pos=(1,1,70,40))
stage1_1=Button('1-1')
stage1_2=Button('1-2')
stage1_3=Button('1-3')

def centralize(mylist,y=screenheight//2,midpoint = screenwidth//2,leftshiftvalue=10):
    leftshiftnum = len(mylist)%2
    centralnum=len(mylist)//2
    if leftshiftnum: #is 1, central button
        x = midpoint - buttonwidth//2 - (buttonwidth+leftshiftvalue)*centralnum
        for button in mylist:
            button.pos = (x,y,buttonwidth,buttonheight)
            x+= leftshiftvalue+buttonwidth
    else:
        x=midpoint+leftshiftvalue//2-(buttonwidth+leftshiftvalue)*centralnum
        for button in mylist:
            button.pos = (x,y,buttonwidth,buttonheight)
            x+= leftshiftvalue+buttonwidth

home_buttons = [startgame,howtoplay,tutorial]
centralize(home_buttons)

def drawhome(click=(0,0)):
    window.blit(homebackground,(0,0))
    for button in home_buttons:
        button.draw()
    pygame.display.update()
stagebuttons=[stage1_1,stage1_2,stage1_3]
centralize(stagebuttons)

def drawstages(click=(0,0)):
    window.blit(homebackground,(0,0))
    back.draw()
    for button in stagebuttons:
        button.draw()
        if inbutton(click,button.pos):
            gameloop(filename='csv_files/'+button.text+'.csv')    
            resetgame()           
    pygame.display.update()

rulestext='''
W -- jump
A -- move left
D -- move right
Right-click -- Use item
Left-click -- Shoot web
Q/E --  Swap items
1,2,3,4 -- Select item from item slots'''

def drawhowtoplay(click=(0,0)):
    window.blit(background,(0,0))
    back.draw()
    font_rules=pygame.font.SysFont('Arial',40,False,False)
    font_rules.set_underline(True)
    text=font_rules.render('How To Play',1,(255,255,255),(0,0,0))
    window.blit(text,((1050-text.get_width())//2,10))
    text=font.render('Lorem ipsum',1,(0,0,0))
    height=text.get_height()
    y = 100
    for sentence in rulestext.split('\n'):
        text=font.render(sentence,1,(255,255,255),(0,0,0))
        window.blit(text,(30,y))
        y+=height+3
    pygame.display.update()

def loopframe(disp_func=lambda:True,buttons=list()):
    global shutdown
    while True:
        clock.tick(10)
        if shutdown:
            break
        click=clicker()
        disp_func(click)
        breakval=False
        for button in buttons:
            if inbutton(click,button.pos):
                # print('clicked back')
                breakval = button.play() or breakval
        if breakval==True:
            break

howtoplay.play = lambda: loopframe(drawhowtoplay,[back])

def resetgame():
    global exiting,time
    for lst in listlist:
        lst.clear()
    exiting=False
    time=0
    
def gameloop(filename='csv_files/tutorial.csv'):
    global exiting,counter,ded
    openmap(filename)
    click=clicker()
    while True:
        ded=False
        clock.tick(30)
        refresh()
        createobj()
        pygame.display.update()
        if player_list[0].health<1:
            exiting=True
            counter-=1
            ded=True
        if shutdown:
            break
        if exiting:
            if ded:
                print('You died. No Highscore')
            else:
                highscore = player_list[0].coin + 20000/time + player_list[0].health*5
                print(highscore)
            break

counter=1
filename='csv_files/'+'1-'+str(counter)+'.csv'
while True:
    clock.tick(10)
    if shutdown:
        break
    click=clicker()
    drawhome()
    if inbutton(click,startgame.pos):
        loopframe(drawstages,[back])
    elif inbutton(click,howtoplay.pos):
        loopframe(drawhowtoplay,[back])
    elif inbutton(click,tutorial.pos):
        gameloop('csv_files/tutorial.csv')        
        resetgame()
  



pygame.quit()




