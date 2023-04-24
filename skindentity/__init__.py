from PIL import Image
from pathlib import Path
from typing import Literal
from hashlib import sha1
from base64 import urlsafe_b64encode

from functools import cache

from skindentity.skin import Skin
from skindentity import renders

renderers = {
    'face':     renders.Face,
    'skin':     renders.Skin,
    'portrait': renders.Portrait,
}

class NoInputError(Exception):
    pass

class Skindentity:

    image_cache: dict = {}
    temp_dir: Path = Path('/tmp/')

    def __init__(self):

        if not self.temp_dir.exists():
            self.temp_dir.mkdir()

        for renderer in renderers.keys():
            directory = self.temp_dir / renderer
            if not directory.exists():
                directory.mkdir()


    def hash(self, string):
        hasher = sha1(string.encode('UTF-8'), usedforsecurity=False)
        return urlsafe_b64encode(hasher.digest()[11:]).decode()

    def render(self,

        slim: bool = False,
        overlay: bool = True,
        margin: int = 0,
        upscale: int = 1,

        name: str = None,
        uuid: str = None,
        blob: str = None,
        url: str = None,

        renderer: Literal['skin', 'face', 'portrait'] = 'skin',
    ) -> Image:

        if url:
            filename = self.hash(url)
        elif uuid:
            filename = self.hash(uuid)
        elif blob:
            filename = self.hash(blob)
        elif name:
            filename = self.hash(name)
        else:
            raise NoInputError("You must provide either a player name, uuid, skin blob or URL")

        if url:
            filename += 'u'
        if uuid:
            filename += 'i'
        if blob:
            filename += 'b'
        if name:
            filename += 'n'
        if slim:
            filename += 's'
        if overlay:
            filename += 'o'
        if margin:
            filename += f'm{margin}'
        if upscale and upscale > 1:
            filename += f'u{upscale}'

        file = self.temp_dir / renderer / f'{filename}.png'

        if file.exists():
            return Image.open(file)

        #if filename in self.image_cache:
        #    return self.image_cache[filename]

        if url:
            skin = Skin.from_url(url)
        elif uuid:
            skin = Skin.from_player_uuid(uuid)
        elif blob:
            skin = Skin.from_blob(blob)
        elif name:
            skin = Skin.from_player_name(name)

        if slim is not None:
            skin.slim = slim

        final_image = renderers[renderer](skin, overlay).render()

        if margin:
            new_size = (final_image.width + (margin*2), final_image.height + (margin*2))
            new = Image.new('RGBA', new_size)
            new.paste(final_image, (margin, margin))
            final_image = new
        if upscale and upscale > 1:
            new_size = (final_image.width*upscale, final_image.height*upscale)
            final_image = final_image.resize(new_size, Image.NEAREST)

        final_image.save(file)
        #self.image_cache[filename] = rendered

        return final_image