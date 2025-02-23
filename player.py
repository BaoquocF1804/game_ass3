import pygame
import os

class Player(pygame.sprite.Sprite):
    GRAVITY = 1
    SPEED = 5
    FPS = 60
    FRICTION_FORCE = 0.5
    ATTACK_RANGE = 32
    WIDTH = 30 * 1.25
    HEIGHT = 50 * 1.25
    ENEMY_DMG = 1
    def __init__(self, x, y, width, height, mode):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.tag = "Player"
        self.velocity = pygame.math.Vector2(0, 0)
        self.fall_count = 0 # virtual gravity

        self.isFacingRight = True
        self.isJump = True
        self.collecting = False
        
        self.move_camera = True
        
        # Cooldown & Timer
        self.dash_cd_timer = 0
        self.dash_cd = 1
        
        self.attack_cd_timer = 0
        self.attack_cd = 0.2
        
        if mode == "Easy":
            self.hp = 5
        elif mode == "Hard":
            self.hp = 1
        self.atk = 1
        
        self.level = 0
        self.score = 0
        
        self.invincible = 3
        self.upgrade_time = 0
        self.stars = 0

        #region Animation
        # Idle
        self.anim_count = 0
        self.anim_state = "Idle"
        self.idle = []
        self.idle.append(pygame.image.load(os.path.join('Assets/Player', 'Idle1.png')))
        self.idle.append(pygame.image.load(os.path.join('Assets/Player', 'Idle2.png')))
        self.idle.append(pygame.image.load(os.path.join('Assets/Player', 'Idle3.png')))
        self.idle.append(pygame.image.load(os.path.join('Assets/Player', 'Idle4.png')))
        self.idle.append(pygame.image.load(os.path.join('Assets/Player', 'Idle5.png')))
        self.idle.append(pygame.image.load(os.path.join('Assets/Player', 'Idle6.png')))
        self.idle.append(pygame.image.load(os.path.join('Assets/Player', 'Idle7.png')))
        self.idle.append(pygame.image.load(os.path.join('Assets/Player', 'Idle8.png')))
        self.idle.append(pygame.image.load(os.path.join('Assets/Player', 'Idle9.png')))
        self.idle.append(pygame.image.load(os.path.join('Assets/Player', 'Idle10.png')))
        self.idle.append(pygame.image.load(os.path.join('Assets/Player', 'Idle11.png')))
        
        # Run
        self.run = []
        self.run.append(pygame.image.load(os.path.join('Assets/Player', 'Run1.png')))
        self.run.append(pygame.image.load(os.path.join('Assets/Player', 'Run2.png')))
        self.run.append(pygame.image.load(os.path.join('Assets/Player', 'Run3.png')))
        self.run.append(pygame.image.load(os.path.join('Assets/Player', 'Run4.png')))
        self.run.append(pygame.image.load(os.path.join('Assets/Player', 'Run5.png')))
        self.run.append(pygame.image.load(os.path.join('Assets/Player', 'Run6.png')))
        self.run.append(pygame.image.load(os.path.join('Assets/Player', 'Run7.png')))
        self.run.append(pygame.image.load(os.path.join('Assets/Player', 'Run8.png')))
        self.run.append(pygame.image.load(os.path.join('Assets/Player', 'Run9.png')))
        self.run.append(pygame.image.load(os.path.join('Assets/Player', 'Run10.png')))
        self.run.append(pygame.image.load(os.path.join('Assets/Player', 'Run11.png')))
        self.run.append(pygame.image.load(os.path.join('Assets/Player', 'Run12.png')))
        
        # Attack
        self.attack = []
        
        # Hit
        self.hit = []
        self.hit.append(pygame.image.load(os.path.join('Assets/Player', 'Hit1.png')))
        self.hit.append(pygame.image.load(os.path.join('Assets/Player', 'Hit2.png')))
        
        # Jump
        self.jump = []
        self.jump.append(pygame.image.load(os.path.join('Assets/Player', 'Jump.png')))
                
        self.anim = []
        self.anim.append(self.idle)
        self.anim.append(self.run)
        self.anim.append(self.attack)
        self.anim.append(self.hit)
        self.anim.append(self.jump)
        
        self.hp_image = pygame.transform.scale(pygame.image.load(os.path.join('Assets/Player', 'hp.png')), (50, 50))
        
        #endregion
        for i in range(len(self.anim)):
            for j in range(len(self.anim[i])):
                self.anim[i][j] = pygame.transform.scale(self.anim[i][j], (width, height))

        self.image = self.idle[0]
        self.mask = pygame.mask.from_surface(self.image)

        self.attack = Attack(self.atk)
    def update(self, keys, objects):
        self.update_input(keys)
        self.update_gravity()
        self.move()
        self.update_animation()
        self.mask = pygame.mask.from_surface(self.image)
        self.vertical_collision(objects, self.velocity.y)
        self.horizontal_collision(objects, self.velocity.x)        
        
        self.update_cd_timer()
        
        if self.attack_cd_timer > 0:
            self.attack.collision(objects)
        
    def draw(self, screen):
        screen.blit(self.image, self.rect)
        self.draw_hp_bar(screen)
        if self.attack_cd_timer > 0:
            pos = self.rect
            if self.isFacingRight:
                pos = (self.rect.x + 4 * self.rect.width / 3, self.rect.y + self.rect.height / 2)
            else:
                pos = (self.rect.x - self.rect.width / 3, self.rect.y + self.rect.height / 2)
            # draw attack range
            self.attack.draw(screen, pos, self.isFacingRight)
    
    def draw_hp_bar(self, screen):
        for i in range(self.hp):
            screen.blit(self.hp_image, (i * self.hp_image.get_width(), 0))
    
    def move(self):
        # self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y
    
    def flip(self):
        self.image = pygame.transform.flip(self.image, True, False)
        self.isFacingRight = not self.isFacingRight
        for i in range(len(self.anim)):
            for j in range(len(self.anim[i])):
                self.anim[i][j] = pygame.transform.flip(self.anim[i][j], True, False)

    def update_input(self, input_keys):
        # horizontal move
        if input_keys[pygame.K_a] or input_keys[pygame.K_LEFT]:
            if self.isFacingRight:
                self.flip()
            if self.velocity.x < -self.SPEED:
                self.velocity.x += self.FRICTION_FORCE
            else:
                self.velocity.x = -self.SPEED
        elif input_keys[pygame.K_d] or input_keys[pygame.K_RIGHT]:
            if not self.isFacingRight:
                self.flip()
            if self.velocity.x > self.SPEED:
                self.velocity.x -= self.FRICTION_FORCE
            else:
                self.velocity.x = self.SPEED
        else:
            if self.velocity.x > 0.1 or self.velocity.x > self.SPEED:
                self.velocity.x -= self.FRICTION_FORCE
            elif self.velocity.x < -0.1 or self.velocity.x < -self.SPEED:
                self.velocity.x += self.FRICTION_FORCE
            else:
                self.velocity.x = 0
            
        # jump
        if input_keys[pygame.K_SPACE] and self.isJump == False and self.fall_count == 0: # make sure player is on the ground
            self.velocity.y = -5
            self.isJump = True
        # attack
        elif input_keys[pygame.K_j] and self.attack_cd_timer <= 0:
            self.attack_cd_timer = self.attack_cd
        # dash
        elif input_keys[pygame.K_k] or input_keys[pygame.K_LSHIFT] or input_keys[pygame.K_LCTRL]:
            if self.dash_cd_timer <= 0:
                self.velocity.x *= 3
                self.dash_cd_timer = self.dash_cd
        # pull_skill
        elif input_keys[pygame.K_e]:
            self.score += 10
        
        elif input_keys[pygame.K_c]:
            self.collecting = True
        else:
            self.collecting = False
    
    def update_cd_timer(self):
        self.dash_cd_timer -= 1 / self.FPS
        self.attack_cd_timer -= 1/self.FPS
        self.invincible -= 1 / self.FPS
    
    #region Physics & Collision 
    def update_gravity(self):
        if self.isJump == True:
            self.velocity.y += min(1, (self.fall_count / self.FPS) * self.GRAVITY)
            self.fall_count += 1
    
    def landed(self):
        self.fall_count = 0
        self.velocity.y = 0
        self.isJump = False

    def hit_head(self):
        self.fall_count = 0
        self.velocity.y = -1
        
    def vertical_collision(self, objects, dy):
        collide_objects = []
        for obj in objects:
            if pygame.sprite.collide_mask(self, obj):
                if obj.get_tag() == "Flag":
                    # end game
                    self.hp = -1
                    print(self.hp)
                if self.invincible <= 0:
                    if obj.get_tag() == "Enemy":
                        self.take_dmg(self.ENEMY_DMG)
                    elif obj.get_tag() == "CannonBall":
                        obj.explode()
                        self.take_dmg(self.ENEMY_DMG)
                if dy > 0:
                    # land on the object
                    self.rect.bottom = obj.rect.top
                    self.landed()
                    
                collide_objects.append(obj)
        return collide_objects
                          
    def collect_item(self, item):
        if item and item.is_collected == False:
            item.kill()
            self.score += item.score
            if self.score % 20 == 0:
                self.level += 1
            item.is_collected = True
    def horizontal_collision(self, objects, dx):
        collide_objects = []
        for obj in objects:
            if pygame.sprite.collide_mask(self, obj):
                # print("Horizontal collide: Player + " + obj.get_tag())
                if obj.get_tag() == "Enemy" or obj.get_tag() == "CannonBall":
                    if self.invincible <= 0:
                        self.take_dmg(self.ENEMY_DMG)
                elif obj.get_tag() == "Obstacle":
                    obj.rect.x += dx
                else:
                    if dx > 0:
                        # right hit the object
                        self.rect.right = obj.rect.left - 0.1
                        self.move_camera = False
                    elif dx < 0:
                        # left hit the object
                        self.rect.left = obj.rect.right + 0.1
                        self.move_camera = False
                collide_objects.append(obj)
            else :
                self.move_camera = True
        return collide_objects
    #endregion
    ############## Getters & Setters ##############
    #region Set & Get
    def set_hp(self, hp):
        self.hp = hp     
    
    def get_hp(self):
        return self.hp
        
    def get_tag(self):
        return self.tag
    
    def get_pos(self):
        return self.rect

    def take_dmg(self, dmg): # Immune when being taken dmg
        pygame.mixer.Sound.play(pygame.mixer.Sound(os.path.join('Assets/Sound', 'be_hit.mp3')))
        if self.anim_state != "Hit":
            self.anim_state = "Hit"
            self.anim_count = 0    
            self.hp -= dmg
            self.invincible = 3
    #endregion
# Ref https://github.com/techwithtim/Python-Platformer/

    #region Animation
    def update_animation(self):
        if self.invincible > 0:
            self.anim_state = "Hit"
        if self.velocity.y > 0.1:
            self.anim_state = "Jump"
        elif self.velocity.x != 0:
            self.anim_state = "Run"
        else:
            self.anim_state = "Idle"
        
        # any state
        if self.anim_state == "Hit":
            self.image = self.hit[int(self.anim_count % 2)]
        # init state
        if self.anim_state == "Idle":
            self.image = self.idle[int(self.anim_count % 11)]
        elif self.anim_state == "Run":
            self.image = self.run[int(self.anim_count % 12)]
        elif self.anim_state == "Jump":
            self.image = self.jump[0]
        elif self.anim_state == "Fall":
            self.image = self.jump[1]        
        self.anim_count += 0.5
        return self.image
    #endregion

class Attack(pygame.sprite.Sprite):
    ATTACK_RANGE = 48
    def __init__(self, atk):
        super().__init__()
        self.atk = atk
        self.isFacingRight = False
        self.image = pygame.image.load(os.path.join('Assets/Player', 'atk.png'))
        self.rect = pygame.Rect(0, 0, self.ATTACK_RANGE, self.ATTACK_RANGE)
        self.image = pygame.transform.scale(self.image, (self.ATTACK_RANGE, self.ATTACK_RANGE))
        self.mask = pygame.mask.from_surface(self.image)

    def collision(self, objects):
        collide_objects = []
        for obj in objects:
            if pygame.sprite.collide_mask(self, obj):
                # print("Collision detect: Attack + " + obj.get_tag())
                if obj.get_tag() == "Enemy":
                    obj.take_dmg(self.atk)
                elif obj.get_tag() == "Cannon":
                    obj.take_dmg(self.atk)
                elif obj.get_tag() == "CannonBall":
                    obj.change_direction(objects)                
                
                collide_objects.append(obj)
                
                if obj.get_tag() == "Breakable Object":
                    obj.break_object()
    
    def draw(self, screen, pos, isFacingRight):
        self.rect = pygame.Rect(pos[0] - self.ATTACK_RANGE / 2, pos[1] - self.ATTACK_RANGE / 2, self.ATTACK_RANGE, self.ATTACK_RANGE)
        if isFacingRight and not self.isFacingRight:
            self.image = pygame.transform.flip(self.image, True, False)
            self.isFacingRight = True
        if not isFacingRight and self.isFacingRight:
            self.image = pygame.transform.flip(self.image, True, False)
            self.isFacingRight = False
        screen.blit(self.image, self.rect)
