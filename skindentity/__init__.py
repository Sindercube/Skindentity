from PIL import Image
from pathlib import Path
#from os import name
from typing import Callable, Union
from hashlib import sha1
from base64 import urlsafe_b64encode

from skindentity.skin import Skin
from skindentity.renders import Renders

class NoInputError(Exception):
    pass

class Skindentity:

    temp_dir = Path('tmp')

    def __init__(self):
        if not self.temp_dir.exists():
            self.temp_dir.mkdir()

    def hash(self, string):
        hasher = sha1(string.encode('UTF-8'), usedforsecurity=False)
        return urlsafe_b64encode(hasher.digest()[:11]).decode()

    def render(self,
        name: str = None,
        uuid: str = None,
        blob: str = None,
        url: str = None,

        slim: bool = None,
        overlay: bool = True,
        margin: int = 0,
        upscale: int = 0,

        renderer: Union['skin', 'face', 'portrait'] = 'skin',
    ) -> Image:


        if name:
            filename = self.hash(name)
        elif uuid:
            filename = self.hash(uuid)
        elif blob:
            filename = self.hash(blob)
        elif url:
            filename = self.hash(url)
        else:
            raise NoInputError("You must provide either a player's name, uuid, skin blob or a URL")

        if slim:
            filename += 's'
        if overlay:
            filename += 'o'
        if margin:
            filename += f'm{margin}'
        if upscale > 1:
            filename += f'u{upscale}'

        file = self.temp_dir / renderer / Path(filename + '.png')

        if file.exists():
            pass
            #image = Image.open(file)
            #return image
        else:
            if not file.parent.exists():
                file.parent.mkdir()

        if name:
            skin = Skin.from_player_name(name)
        elif uuid:
            skin = Skin.from_player_uuid(uuid)
        elif blob:
            skin = Skin.from_blob(blob)
        elif url:
            skin = Skin.from_url(url)

        if slim != None:
            skin.slim = slim

        rendered = Renders(skin, overlay).render(renderer)

        if margin:
            new = Image.new('RGBA', (rendered.width+margin+margin, rendered.height+margin+margin))
            new.paste(rendered, (margin, margin))
            rendered = new
        if upscale > 1:
            rendered = rendered.resize((rendered.width*upscale, rendered.height*upscale), Image.NEAREST)

        rendered.save(file)
        return rendered