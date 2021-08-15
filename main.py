from fastapi import FastAPI, File, UploadFile, Query, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse, HTMLResponse
from PIL import Image, UnidentifiedImageError
from urllib.request import Request, urlopen
from os import getenv
from io import BytesIO
from deta import Deta
from json import loads
from json.decoder import JSONDecodeError
from base64 import b64decode

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

async def api_template(render_function, drive, player, skin_url, skin_base64, slim):

    if player:
        try:
            url, pot_slim = skin_from_player(player)
            filename = url.split('/')[-1]
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
        filename = skin_url.split('/')[-1]
        try:
            skin = skin_from_url(skin_url)
        except UrlError:
            return HTTPException(status_code=404, detail="Invalid URL")
        except ImageSizeError:
            return HTTPException(status_code=404, detail="Image must be 64x64 pixels large")
    elif skin_base64:
        b = BytesIO(b64decode(skin_base64))
        try:
            skin = Image.open(b)
        except UrlError:
            return HTTPException(status_code=404, detail="Invalid File, must be Image")
        filename = skin_base64[1:12]
    else:
        return HTTPException(status_code=404, detail="You must specify a Player Name, Skin URL or Skin File.")

    stored = False
    pot_image = drive.get(filename)
    if pot_image:
        image = Image.open(pot_image)
        stored = True
    else:
        image = render_function(skin, slim)

    if not stored:
        byte_result = BytesIO()
        image.save(byte_result, format='PNG')
        byte_result.seek(0)
        drive.put(filename, byte_result)

    # post-processing, eventually

    byte_result = BytesIO()
    image.save(byte_result, format='PNG')
    byte_result.seek(0)
    return StreamingResponse(byte_result, media_type="image/png")

def template_args(player_name: str = Query(None, max_length=16), skin_url: str = Query(None, max_length=128), skin_base64: str = Query(None, max_length=16*1024), slim: bool = Query(None)):
    return [player_name, skin_url, skin_base64, slim]

with open('index.html', 'r') as file:
    html_content = file.read()

@app.get('/')
async def landing(args: template_args = Depends()):
    return HTMLResponse(content=html_content, status_code=200)

@app.get('/skin/')
async def skin(args: template_args = Depends()):
    return await api_template(lambda x, *_: x, deta.Drive('skins'), *args)

@app.get('/portrait/')
async def portrait(args: template_args = Depends()):
    return await api_template(skin_to_portrait, deta.Drive('portraits'), *args)

@app.get('/profile/')
async def profile(args: template_args = Depends()):
    return await api_template(skin_to_profile, deta.Drive('profiles'), *args)