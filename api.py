from fastapi import Depends, FastAPI, Query, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from io import BytesIO

from skindentity import Skindentity

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="html")
sk = Skindentity()

def template_args(name:    str  = Query(None, description="The Username of the Player to use.", max_length=16),
                  uuid:    str  = Query(None, description="The UUID of the Player to use.", max_length=32),
                  blob:    str  = Query(None, description="Base64 hash to use.", max_length=16*1024),
                  url:     str  = Query(None, description="What URL to use.", max_length=128),
                  slim:    bool = Query(False, description="Whether the skin uses the slim body type."),
                  overlay: bool = Query(True, description="Whether or not to show the skin's overlay layers."),
                  margin:  int  = Query(0, description="How many pixels around the image to make transparent. (1 to 8)", ge=1, le=8),
                  upscale: int  = Query(1, description="How many times to increase the size of a pixel. (2 to 8)", ge=2, le=8)
    ):
    return [name, uuid, blob, url, slim, overlay, margin, upscale]

@app.get("/", response_class=HTMLResponse)
async def landing(request: Request):
    return templates.TemplateResponse("index.html", {'request': request, 'renders': ['portrait', 'face', 'skin']})

def get_render(renderer, *args):
    result = sk.render(*args, renderer)
    byte_result = BytesIO()
    result.save(byte_result, format='PNG')
    byte_result.seek(0)
    return StreamingResponse(byte_result, media_type="image/png")

@app.get('/skin/')
async def skin(args: template_args = Depends()):
    return get_render('skin', *args)

@app.get('/face/')
async def face(args: template_args = Depends()):
    return get_render('face', *args)

@app.get('/portrait/')
async def portrait(args: template_args = Depends()):
    return get_render('portrait', *args)