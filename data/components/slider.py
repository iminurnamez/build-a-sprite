import pygame as pg

from ..prepare import GFX
from ..components.labels import Button, ButtonGroup


class Slider(pg.sprite.Sprite):
    def __init__(self, midtop, value, max_value, *groups):
        super(Slider, self).__init__(*groups)
        self.value = value
        self.max_value = max_value
        self.rect = pg.Rect(0, 0, 250, 80)
        self.rect.midtop = midtop
        w, h = self.rect.size
        self.bar = GFX["slider-bar"]
        self.tab = GFX["slider-tab"]
        self.bar_rect = self.bar.get_rect(center=(w//2, 20))
        self.tab_rect = self.tab.get_rect(center=self.bar_rect.center)
        self.slide_rect = self.bar_rect.inflate(-16, 0)
        self.tab_boundary = self.slide_rect.inflate(self.tab_rect.width, 0)
        self.grabbed = False
        self.set_tab()
        self.make_buttons()
        self.image = pg.Surface(self.rect.size).convert_alpha()

    def make_buttons(self):
        self.buttons = ButtonGroup()  
        right_idle = GFX["arrow-right-dim"]
        right_hover = GFX["arrow-right-bright"]
        left_idle = GFX["arrow-left-dim"]
        left_hover = GFX["arrow-left-bright"]
        b_size = 38
        left1 = self.bar_rect.left - (b_size + 5)
        left2 = self.bar_rect.right + 5
        Button((left1, 0), self.buttons, button_size=(b_size, b_size), 
                    idle_image=left_idle, hover_image=left_hover,
                    call=self.decrease_value)
        Button((left2, 0), self.buttons, button_size=(b_size, b_size), 
                    idle_image=right_idle, hover_image=right_hover,
                    call=self.increase_value)
    
    def increase_value(self, *args):
        self.value += 1
        if self.value > self.max_value:
            self.value = self.max_value
        self.set_tab()
        
    def decrease_value(self, *args):
        self.value -= 1
        if self.value < 0:
            self.value = 0
        self.set_tab()
        
    def set_tab(self):
        slide = self.value / float(self.max_value)
        self.tab_rect.centerx = self.slide_rect.left + (self.slide_rect.w * slide)
        
    def get_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            adj_pos = event.pos[0] - self.rect.left, event.pos[1] - self.rect.top
            if self.tab_rect.collidepoint(adj_pos):
                self.grabbed = True
                self.x_grab_offset = self.tab_rect.centerx - adj_pos[0]
                
        elif event.type == pg.MOUSEBUTTONUP:
            if self.grabbed:
                self.grabbed = False
        self.buttons.get_event(event)
        
    def update(self, mouse_pos):
        if self.grabbed:
            cx = (mouse_pos[0] - self.rect.left) + self.x_grab_offset
            w = float(self.slide_rect.width)
            self.tab_rect.centerx = cx
            self.tab_rect.clamp_ip(self.tab_boundary)
            slide = (self.tab_rect.centerx - self.slide_rect.left) / w
            self.value = int(slide * self.max_value)
        self.make_image()
        adj_pos = mouse_pos[0] - self.rect.left, mouse_pos[1] - self.rect.top
        self.buttons.update(adj_pos)
        
    def make_image(self):
        self.image.fill((0, 0, 0, 0))
        self.image.blit(self.bar, self.bar_rect)
        self.image.blit(self.tab, self.tab_rect)
        self.buttons.draw(self.image)
        
    def draw(self, surface):
        surface.blit(self.image, self.rect)
        
        
