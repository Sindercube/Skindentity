from fastapi import FastAPI, File, UploadFile, Query, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse, HTMLResponse
from PIL import Image, UnidentifiedImageError
from urllib.request import Request, urlopen
from os import getenv, listdir, mkdir
from io import BytesIO
from deta import Deta
from json import loads
from json.decoder import JSONDecodeError
from base64 import b64decode, binascii

from renders import *

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
        image = old_to_new_skin(image)
    if image.size != (64, 64):
        raise ImageSizeError
    return image

async def api_template(render_function, path, player, skin_url, skin_base64, slim):

    if player:
        try:
            url, pot_slim = skin_from_player(player)
            filename = url.split('/')[-1][-12:-1]
            try:
                skin = skin_from_url(url)
            except UrlError:
                return HTTPException(status_code=404, detail="Invalid URL")
            except ImageSizeError:
                return HTTPException(status_code=404, detail="Image must be 64x64 pixels large")
            if slim == None:
                slim = pot_slim
        except UnknownPlayerError:
            return HTTPException(status_code=404, detail="Unknown player")
    elif skin_url:
        filename = skin_url.split('/')[-1][-12:-1]
        try:
            skin = skin_from_url(skin_url)
        except UrlError:
            return HTTPException(status_code=404, detail="Invalid URL")
        except ImageSizeError:
            return HTTPException(status_code=404, detail="Image must be 64x64 pixels large")
    elif skin_base64:
        try:
            b = BytesIO(b64decode(skin_base64 + '='))
        except binascii.Error:
            b = BytesIO(b64decode(skin_base64))
        try:
            skin = Image.open(b)
        except UrlError:
            return HTTPException(status_code=404, detail="Invalid File, must be Image")
        filename = skin_base64[-12:-1]
    else:
        return HTTPException(status_code=404, detail="You must specify a Player Name, Skin URL or Skin File.")

    if not filename.endswith('.png'):
        filename += '.png'

    try:
        files = listdir('/tmp/'+path)
    except FileNotFoundError:
        mkdir('/tmp/'+path)
        files = []
    if filename in files:
        image = Image.open('/tmp/'+path+filename)
    else:
        image = render_function(skin, slim)
        image.save('/tmp/'+path+filename)

    # post-processing, eventually

    byte_result = BytesIO()
    image.save(byte_result, format='PNG')
    byte_result.seek(0)
    return StreamingResponse(byte_result, media_type="image/png")

def template_args(player_name: str = Query(None, max_length=16), skin_url: str = Query(None, max_length=128), skin_base64: str = Query(None, max_length=16*1024), slim: bool = Query(None)):
    return [player_name, skin_url, skin_base64, slim]

@app.get('/skin/')
async def skin(args: template_args = Depends()):
    return await api_template(lambda x, *_: x, 'skins/', *args)

@app.get('/portrait/')
async def portrait(args: template_args = Depends()):
    return await api_template(skin_to_portrait, 'portraits/' , *args)

@app.get('/face/')
async def face(args: template_args = Depends()):
    return await api_template(skin_to_face, 'profiles/', *args)