from PIL import Image
from base64 import b64decode
from requests import get
from dataclasses import dataclass
from io import BytesIO
from json import loads

class ImageSizeError(Exception):
    pass
class UnknownPlayerError(Exception):
    pass

def _url_to_json(url: str) -> dict:
    return get(url).json()

class Skin:

    def __init__(self, image: Image, slim: bool = False):
        if image.size == (64, 32):
            image = self._old_to_new_skin(image)
        if image.size != (64, 64):
            raise ImageSizeError

        self.image = image
        self.slim = slim

    @classmethod
    def from_url(cls, url: str):

        response = get(url)#, headers={'User-Agent':' Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0) Gecko/20100101 Firefox/12.0'})
        image = Image.open(BytesIO(response.content))
        print(response.content)

        return cls(image)

    @classmethod
    def from_blob(cls, blob: str):
        data = loads(b64decode(blob).decode('utf-8'))

        skin = cls.from_url(data['textures']['SKIN']['url'])
        skin.slim = data.get('textures', {}).get('SKIN', {}).get('metadata', {}).get('model', None) == 'slim'

        return skin

    @classmethod
    def from_player_uuid(cls, uuid: str):
        data = _url_to_json('https://sessionserver.mojang.com/session/minecraft/profile/' + uuid)
        if not 'properties' in data:
            raise UnknownPlayerError
        blob = data['properties'][0]['value']

        return cls.from_blob(blob)

    @classmethod
    def from_player_name(cls, player_name: str):
        data = _url_to_json('https://api.mojang.com/users/profiles/minecraft/' + player_name)
        if not 'id' in data:
            raise UnknownPlayerError

        return cls.from_player_uuid(data['id'])

    def _old_to_new_skin(self, image: Image) -> Image:
        final_image = Image.new('RGBA', (64, 64))
        leg_copy = image.crop((0, 16, 16, 32))
        arm_copy = image.crop((40, 16, 56, 32))
        final_image.paste(image, (0, 0))
        final_image.paste(leg_copy, (16, 48))
        final_image.paste(arm_copy, (32, 48))
        return final_image