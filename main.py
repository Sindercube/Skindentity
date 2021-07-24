from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from io import BytesIO
from PIL import Image, ImageOps, UnidentifiedImageError
from urllib.request import urlopen
from os import environ, listdir

app = FastAPI()
true_api_key = environ['API_KEY']
converted_skins = []

@app.get('/')
def return_profile_image(skin_url: str = Query(None, max_length=102), api_key: str = Query(None, max_length=20)):
    global converted_skins
    try:
        skin_id = ''.join(list(skin_url.split('http://textures.minecraft.net/texture/')[1])[0:6])
    except IndexError:
        return "Skin image must be provided by https://textures.minecraft.net"
    if skin_id in converted_skins:
        return FileResponse("skins/"+skin_id+".png")
    if api_key != true_api_key:
        return "Invalid API key"
    try:
        skin_image = Image.open(urlopen(skin_url)).convert('RGBA')
    except ValueError:
        return "Unknown URL type: {}".format(skin_url)
    except UnidentifiedImageError:
        return "URL doesn't point to an image"
    head_image = skin_image.crop((8, 8, 16, 16))
    final_image = Image.new('RGBA', (12, 12))
    final_image.paste(head_image, (2, 2))
    # resize the overlay image manually because Image.alpha_composite requires that
    temp_overlay_image = skin_image.crop((40, 8, 48, 16))
    overlay_image = Image.new('RGBA', (12, 12))
    overlay_image.paste(temp_overlay_image, (2, 2))
    final_image = Image.alpha_composite(final_image, overlay_image)
    final_image.resize((360, 360), Image.NEAREST).save("skins/"+skin_id+".png", 'PNG')
    converted_skins.append(skin_id)
    return FileResponse("skins/"+skin_id+".png")