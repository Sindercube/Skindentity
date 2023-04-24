from PIL import Image, ImageEnhance
from skindentity import Skin

class Renderer:

    def __init__(self, skin: Skin, overlay: bool):
        self.image = skin.image
        self.slim = skin.slim
        self.overlay = overlay
    
    def _render_side(self, main_pos: tuple, overlay_pos: tuple) -> Image:
        if len(main_pos) == 2: main_pos += tuple(i+8 for i in main_pos)
        if len(overlay_pos) == 2: overlay_pos += tuple(i+8 for i in overlay_pos)

        result = self.image.crop(main_pos).convert("RGBA")
        part = Image.new('RGBA', (result.width+2, result.height+2), (0, 0, 0, 0))
        part.paste(result, (1, 1))
        
        if self.overlay:
            overlay = self.image.crop(overlay_pos).convert("RGBA")
            part.paste(overlay, (2, 1), overlay)
            part.paste(overlay, (0, 1), overlay)
        
        enhancer = ImageEnhance.Brightness(part)
        enhanced_im = enhancer.enhance(0.75)

        return enhanced_im.resize(( int(part.width/2)+1, part.height ), Image.NEAREST)

    def _render_face(self, main_pos: tuple, overlay_pos: tuple) -> Image:
        if len(main_pos) == 2: main_pos += tuple(i+8 for i in main_pos)
        if len(overlay_pos) == 2: overlay_pos += tuple(i+8 for i in overlay_pos)

        result = self.image.crop(main_pos).convert("RGBA")
        if self.overlay:
            overlay = self.image.crop(overlay_pos).convert("RGBA")
            result = Image.alpha_composite(result, overlay)
        return result

class Skin(Renderer):

    def render(self):
        return self.image

class Face(Renderer):

    def render(self):
        return self._render_face((8, 8), (40, 8))

class Portrait(Renderer):

    def render(self):

        final_image = Image.new('RGBA', (24, 24))

        head_front = self._render_face((8, 8), (40, 8))
        final_image.paste(head_front, (10, 2))
        head_side = self._render_side((0, 8), (32, 8))
        final_image.paste(head_side, (5, 1), head_side)

        body_mid = self._render_face((20, 20, 28, 32), (20, 36, 28, 48))
        final_image.paste(body_mid, (9, 11))

        if self.slim:
            arm_left = self._render_face((36, 52, 39, 64), (52, 52, 55, 64))
        else:
            arm_left = self._render_face((36, 52, 40, 64), (52, 52, 56, 64))
        final_image.paste(arm_left, (18, 11))

        if self.slim:
            arm_right = self._render_face((44, 20, 47, 32), (44, 36, 47, 48))
            final_image.paste(arm_right, (5, 11))
            arm_right_side = self._render_side((40, 20, 44, 32), (40, 36, 44, 48))
            final_image.paste(arm_right_side, (2, 10), arm_right_side)
        else:
            arm_right = self._render_face((44, 20, 48, 32), (44, 36, 48, 48))
            final_image.paste(arm_right, (4, 11))
            arm_right_side = self._render_side((40, 20, 44, 32), (40, 36, 44, 48))
            final_image.paste(arm_right_side, (1, 10), arm_right_side)

        outline_image = Image.new('RGBA', (24, 24), (0, 0, 0, 0))

        outline_image.paste(final_image, (-1, 0), final_image)
        outline_image.paste(final_image, (0, -1), final_image)
        outline_image.paste(final_image, (1, 0), final_image)
        outline_image.paste(final_image, (0, 1), final_image)

        enhancer = ImageEnhance.Brightness(outline_image)
        enhanced_im = enhancer.enhance(0.25)
        enhanced_im.paste(final_image, (0, 0), final_image)
        bar = Image.new('RGBA', (24, 1), (0, 0, 0, 0))
        enhanced_im.paste(bar, (0, 23))

        return enhanced_im