from PIL import Image
from base64 import b64decode
from requests import get
from io import BytesIO
from json import loads

class ImageSizeError(Exception):
    pass
class UnknownPlayerError(Exception):
    pass

def _url_to_json(url: str) -> dict:
    return get(url).json()

class Skin:

    image: Image
    slim: bool

    def __init__(self, image: Image, slim: bool = False):
        if image.size == (64, 32):
            image = self._old_to_new_skin(image)
        if image.size != (64, 64):
            raise ImageSizeError('Skin should be 64x64 pixels in size.')

        self.image = image
        self.slim = slim

    @classmethod
    def from_url(cls, url: str):
        try:
            response = get(url, headers={'User-Agent':'Sindercube/'})
        except Exception:
            raise UnknownPlayerError(f"Couldn't get image from url '{url}'.")
        image = Image.open(BytesIO(response.content))

        return cls(image)

    @classmethod
    def from_blob(cls, blob: str):
        data = loads(b64decode(blob).decode('utf-8'))
        skin_data = data.get('textures', {}).get('SKIN', {})
        if not skin_data:
            raise UnknownPlayerError("Blob contains no skin information.")

        skin = cls.from_url(skin_data.get('url', None))
        skin.slim = skin_data.get('metadata', {}).get('model', None) == 'slim'

        return skin

    @classmethod
    def from_player_uuid(cls, uuid: str):
        data_url = 'https://sessionserver.mojang.com/session/minecraft/profile/' + uuid
        data = _url_to_json(data_url)
        if 'properties' not in data:
            raise UnknownPlayerError(f"Couldn't find any players with the uuid '{uuid}'.")
        blob = data['properties'][0]['value']

        return cls.from_blob(blob)

    @classmethod
    def from_player_name(cls, player_name: str):
        data_url = 'https://api.mojang.com/users/profiles/minecraft/' + player_name
        data = _url_to_json(data_url)
        if 'id' not in data:
            raise UnknownPlayerError(f"Couldn't find any players named '{player_name}'.")

        return cls.from_player_uuid(data['id'])

    def _old_to_new_skin(self, image: Image) -> Image:
        final_image = Image.new('RGBA', (64, 64))
        leg_copy = image.crop((0, 16, 16, 32))
        arm_copy = image.crop((40, 16, 56, 32))
        final_image.paste(image, (0, 0))
        final_image.paste(leg_copy, (16, 48))
        final_image.paste(arm_copy, (32, 48))
        # TODO: make black (previously transparent) parts of the skin actually transparent 
        return final_image