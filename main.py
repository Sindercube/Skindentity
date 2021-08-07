from fastapi import FastAPI, Query, HTTPException, Depends
from fastapi.responses import StreamingResponse
from PIL import Image, UnidentifiedImageError
from urllib.request import Request, urlopen
from os import getenv
from io import BytesIO
from deta import Deta
from json import loads
from json.decoder import JSONDecodeError
from base64 import b64decode

import renders

class ImageSizeError(Exception):
    pass
class UrlError(Exception):
    pass
class ArgumentError(Exception):
    pass
class UnknownPlayerError(Exception):
    pass

app = FastAPI()
deta = Deta(getenv('DETA_PROJECT_KEY'))

def skin_from_player(player):
    try:
        id_json = loads(urlopen('https://api.mojang.com/users/profiles/minecraft/' + player).read())
    except JSONDecodeError:
        raise UnknownPlayerError
    if not id_json:
        raise UnknownPlayerError
    data_json = loads(urlopen('https://sessionserver.mojang.com/session/minecraft/profile/' + id_json['id']).read())
    data = data_json['properties'][0]['value']
    decoded_json = loads(b64decode(data).decode('utf-8'))

    link = decoded_json['textures']['SKIN']['url']
    try:
        slim = decoded_json['textures']['SKIN']['metadata']['model'] == 'slim'
    except KeyError:
        slim = False
    return link, slim

def skin_from_url(url):
    try:
        req = Request(url=url, headers={'User-Agent':' Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0) Gecko/20100101 Firefox/12.0'})
        file = urlopen(req)
    except ValueError:
        raise UrlError
    try:
        image = Image.open(file).convert('RGBA')
    except UnidentifiedImageError:
        raise UrlError
    if image.size == (64, 32):
        image = renders.old_to_new_skin(image)
    if image.size != (64, 64):
        raise ImageSizeError
    return image

def api_template(args, render_function, drive):
    player, url, slim = args
    
    if not player and not url:
        return HTTPException(status_code=404, detail="You must specify a player or a skin URL")
    if player:
        try:
            skin_data = skin_from_player(player)
            url = skin_data[0]
            if slim == None:
                slim = skin_data[1]
        except UnknownPlayerError:
            return HTTPException(status_code=404, detail="Unknown player")
    print(slim)
    filename = url.split('/')[-1]
    if not filename.endswith('.png'):
        filename = filename.rsplit('.')[0]+'.png'
    # get potential image

    pot_image = drive.get(filename)
    if pot_image:
        image = Image.open(pot_image)
        byte_result = BytesIO()
        image.save(byte_result, format='PNG')
        byte_result.seek(0)

        return StreamingResponse(byte_result, media_type="image/png")
    # get actual image

    try:
        skin_image = skin_from_url(url)
    except UrlError:
        return HTTPException(status_code=404, detail="Invalid URL")
    except ImageSizeError:
        return HTTPException(status_code=404, detail="Image must be 64x64 pixels large")

    image = render_function(skin_image, slim)
    # save to drive
    byte_result = BytesIO()
    image.save(byte_result, format='PNG')
    byte_result.seek(0)
    drive.put(filename, byte_result)
    # return
    byte_result = BytesIO()
    image.save(byte_result, format='PNG')
    byte_result.seek(0)
    return StreamingResponse(byte_result, media_type="image/png")

def template_args(player: str = Query(None, max_length=16), skin_url: str = Query(None, max_length=110), slim: bool = Query(None)):
    return [player, skin_url, slim]

@app.get('/portrait/')
async def portrait(args: template_args = Depends()):
    return api_template(args, renders.skin_to_portrait, deta.Drive('portraits'))

@app.get('/profile/')
async def profile(args: template_args = Depends()):
    return api_template(args, renders.skin_to_profile, deta.Drive('profiles'))