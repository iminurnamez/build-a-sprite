import pygame as pg

from .. import prepare
from .. components.labels import Label, Button, ButtonGroup


class Adjuster(pg.sprite.Sprite):
    def __init__(self, midtop, text, value_name, limit, values_dict, *groups):
        super(Adjuster, self).__init__(*groups)
        self.text = text
        self.name = value_name
        self.limit = limit
        self.values = values_dict
        self.make_buttons(midtop)
    
    def make_buttons(self, midtop):
        right_idle = prepare.GFX["arrow-right-dim"]
        right_hover = prepare.GFX["arrow-right-bright"]
        left_idle = prepare.GFX["arrow-left-dim"]
        left_hover = prepare.GFX["arrow-left-bright"]
        
        self.buttons = ButtonGroup()
        self.labels = pg.sprite.Group()
        b_size = 32
        space = 50
        left2 = b_size + space
        Button((left2, 0), self.buttons, button_size=(b_size, b_size), 
                    idle_image=right_idle, hover_image=right_hover,
                    call=self.increase_value)
        Button((0, 0), self.buttons, button_size=(b_size, b_size), 
                    idle_image=left_idle, hover_image=left_hover,
                    call=self.decrease_value)
        cx = b_size + (space // 2)            
        Label(self.text, {"center": (cx, b_size//2)}, self.labels)
        self.rect = pg.Rect(0, 0, space + (b_size * 2), b_size)
        self.rect.center = midtop
        self.image = pg.Surface(self.rect.size).convert_alpha()
        
    def draw_image(self):
        self.image.fill((0, 0, 0, 0))
        self.buttons.draw(self.image)
        self.labels.draw(self.image)
        
    def increase_value(self, *args):
        self.values[self.name] += 1
        if self.values[self.name] == self.limit:
            self.values[self.name] = 0

    def decrease_value(self, *args):
        self.values[self.name] -= 1
        if self.values[self.name] < 0:
            self.values[self.name] = self.limit - 1
        
    def get_event(self, event):
        self.buttons.get_event(event)
        
    def update(self, mouse_pos):
        x, y = mouse_pos
        adj_pos = x - self.rect.left, y - self.rect.top
        self.buttons.update(adj_pos)
        self.draw_image()
        
    def draw(self, surface):
        surface.blit(self.image, self.rect)

        
