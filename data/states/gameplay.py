import pygame as pg

from .. import tools, prepare
from ..tools import strip_from_sheet
from ..prepare import GFX
from ..components.adjuster import Adjuster
from ..components.slider import Slider
from ..components.labels import Button, ButtonGroup
from ..components.animation import Animation, Task


def load_images(sheet, strip_size, num_columns, num_rows,
                                                 sprite_size, sprites_per_row):
    d = {}
    strips = strip_from_sheet(sheet, (0, 0), strip_size, num_columns,
                                                    num_rows)
    for i, strip in enumerate(strips):
        d[i] = {}
        imgs = strip_from_sheet(strip, (0, 0), sprite_size, sprites_per_row)
        for j, img in enumerate(imgs):        
            d[i][j] = img
    return d
    
HAIR = load_images(GFX["hair"], (1020, 116), 1, 5, (68, 116), 15)                                          
HATS = load_images(GFX["hats"], (816, 116), 1, 34, (68, 116), 12)
MASKS = load_images(GFX["masks"], (408, 116), 1, 34, (68, 116), 6)
FACIAL_HAIR = load_images(GFX["facial-hair"], (1088, 116), 1, 5, (68, 116), 16)
TOPS = load_images(GFX["tops"], (1496, 116), 1, 34, (68, 116), 22)
BOTTOMS = load_images(GFX["bottoms"], (544, 116), 1, 34, (68, 116), 8)
SKIN = strip_from_sheet(GFX["skin"], (0, 0), (68, 112), 12)
EYES = strip_from_sheet(GFX["eyes"], (0, 0), (68, 112), 17)
SHOES = strip_from_sheet(GFX["shoes"], (0, 0), (68, 114), 17, 2)
SPECIAL_MASKS = strip_from_sheet(GFX["special-masks"], (0, 0), (68, 116), 12, 2)


class Gameplay(tools._State):
    def __init__(self):
        super(Gameplay, self).__init__()
        self.animations = pg.sprite.Group()
        self.person_rect = pg.Rect(0, 0, 68, 116)
        self.person_rect.midbottom = prepare.SCREEN_RECT.centerx, 320
        alterables = ["skin_color", "eye_color", "top_color", "top_style", 
                            "bottom_color", "bottom_style", "shoe_color", 
                            "hair_color", "hair_style", "facial_hair_color", 
                            "facial_hair_style", "mask_color", "mask_style",
                            "hat_color", "hat_style", "special_mask_color"]
        alter_cats = [SKIN, EYES, TOPS, TOPS[0], BOTTOMS, BOTTOMS[0], 
                            SHOES, HAIR, HAIR[0], FACIAL_HAIR, FACIAL_HAIR[0],
                            MASKS, MASKS[0], HATS, HATS[0], SPECIAL_MASKS]
        self.outfit = {alterable: 0 for alterable in alterables}
        self.limits = {a: len(c) for a, c in zip(alterables, alter_cats)}
        names = ["hat", "hair", "skin", "eyes", "facial", "top", 
                        "bottom", "shoes", "mask", "special_mask"]
        sub_cats = [
                ("hat_color", "hat_style"),
                ("hair_color", "hair_style"),
                ("skin_color",),
                ("eye_color",),
                ("facial_hair_color", "facial_hair_style"),
                ("top_color", "top_style"),
                ("bottom_color", "bottom_style"),
                ("shoe_color",),
                ("mask_color", "mask_style"),
                ("special_mask_color",)]
        self.categories = {name: sub_cat
                                    for name, sub_cat in zip(names, sub_cats)}
        self.active = {name: True for name in names}
        inactive = ("mask", "special_mask")
        for i in inactive:
            self.active[i] = False
        
        self.make_category_buttons()
        self.current_adjusters = None
        self.category = None
        self.current_button_topleft = prepare.SCREEN_RECT.centerx - 38, 350
        self.make_buttons()
        self.make_sliders()
        self.image_num = 0
        
    def make_buttons(self):
        self.buttons = ButtonGroup()
        Button((100, 620), self.buttons, button_size=(76, 76),
                    idle_image=prepare.GFX["camera"], call=self.save_image)
        b2 = Button((200, 620), self.buttons, button_size=(76, 76),
                           idle_image=prepare.GFX["mountains"],
                           call=self.change_category, args="bg_color")
        b2.home_pos = b2.rect.topleft
        self.button_dict["bg_color"] = b2
        
    def save_image(self, *args):
        surf = pg.Surface(self.person_rect.size).convert_alpha()
        surf.fill((0,0,0,0))
        self.draw_image(surf, (0, 0))
        self.image_num += 1
        pg.image.save(surf, "image{}.png".format(self.image_num))
        
    def make_category_buttons(self):
        self.adjusters = {}
        self.button_dict = {}
        self.category_buttons = ButtonGroup()
        categories = ["hat", "hair", "skin", "eyes", "facial", "top", "bottom",
                             "shoes", "mask", "special_mask"]
        button_images = strip_from_sheet(GFX["button-strip"],
                                                              (0, 0), (76, 76), 10)
        left = 292
        top = 5
        cx = prepare.SCREEN_RECT.centerx 
        for c, img in zip(categories, button_images):
            b = Button((left, top), self.category_buttons, button_size=(76, 76),
                        idle_image=img, call=self.change_category,
                        args=c)
            b.home_pos = (left, top)
            self.button_dict[c] = b
            left += 80

            sub_top = 450
            title = "Color"
            self.adjusters[c] = pg.sprite.Group()
            for sub_cat in self.categories[c]:
                adj = Adjuster((cx, sub_top), title, sub_cat,
                                       self.limits[sub_cat], self.outfit,
                                       self.adjusters[c])
                sub_top += 65
                title = "Style"
            button_pos = (cx - 38, sub_top)
            toggler = Button(button_pos, self.adjusters[c], button_size=(76, 38),
                                      idle_image=GFX["toggle"], call=self.toggle_category, args=c)

    def change_category(self, category):
        new_button = self.button_dict[category]
        if self.category:
            old_button = self.button_dict[self.category]
            x, y = old_button.home_pos
            ani = Animation(x=x, y=y, duration=350, transition="linear",
                                    round_values=True)
            ani.start(old_button.rect)
            self.animations.add(ani)
        if self.category and self.category == category:
            self.current_adjusters = None
            self.category = None
        else:
            self.current_adjusters = self.adjusters[category]
            bx, by = self.current_button_topleft
            ani2 = Animation(x=bx, y=by, duration=350, transition="linear",
                                      round_values=True)
            ani2.start(new_button.rect)
            self.animations.add(ani2)
            self.category = category

    def toggle_category(self, category):
        self.active[category] = not self.active[category]
        
    def make_sliders(self):
        self.sliders = {}
        self.adjusters["bg_color"] = pg.sprite.Group()
        cx = prepare.SCREEN_RECT.centerx
        top = 450
        for color in ("red", "green", "blue"):
            s = Slider((cx, top), 0, 255)
            self.sliders[color] = s
            self.adjusters["bg_color"].add(s)
            top += s.rect.h
            
    def draw_image(self, surface, rect):
        d = self.outfit
        images = [
                ("hair", HAIR[d["hair_color"]][d["hair_style"]]),
                ("skin", SKIN[d["skin_color"]]),
                ("eyes", EYES[d["eye_color"]]),
                ("hat", HATS[d["hat_color"]][d["hat_style"]]),
                ("top", TOPS[d["top_color"]][d["top_style"]]),
                ("bottom", BOTTOMS[d["bottom_color"]][d["bottom_style"]]),
                ("facial", FACIAL_HAIR[d["facial_hair_color"]][d["facial_hair_style"]]),
                ("mask", MASKS[d["mask_color"]][d["mask_style"]]),
                ("special_mask", SPECIAL_MASKS[d["special_mask_color"]]),
                ("shoes", SHOES[d["shoe_color"]])]

        for name, img in images:
            if self.active[name]:
                surface.blit(img, rect)

    def startup(self, persitent):
        self.persist = persistent

    def get_event(self,event):
        if event.type == pg.QUIT:
            self.quit = True
        elif event.type == pg.KEYUP:
            if event.key == pg.K_ESCAPE:
                self.quit = True
        self.category_buttons.get_event(event)
        self.buttons.get_event(event)
        if self.current_adjusters:
            for a in self.current_adjusters:
                a.get_event(event)

    def update(self, dt):
        self.animations.update(dt)
        mouse_pos = pg.mouse.get_pos()
        if self.current_adjusters:
            self.current_adjusters.update(mouse_pos)
        self.category_buttons.update(mouse_pos)
        self.buttons.update(mouse_pos)
        self.bg_color = tuple((self.sliders[c].value for c in ("red", "green", "blue")))
    
    def draw(self, surface):
        surface.fill(self.bg_color)
        self.draw_image(surface, self.person_rect)
        self.category_buttons.draw(surface)
        self.buttons.draw(surface)
        if self.current_adjusters:
            self.current_adjusters.draw(surface)
