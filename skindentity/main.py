from fastapi import FastAPI, Query, Request, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from io import BytesIO
from enum import Enum

from skindentity import Skindentity
#from skindentity.skin import UnknownPlayerError

class Types(Enum):
    @classmethod
    def list(cls):
        return [e.value for e in cls]

class RenderTypes(Types):
    skin = 'skin'
    face = 'face'
    portrait = 'portrait'

class InputTypes(Types):
    name = 'name'
    uuid = 'uuid'
    blob = 'blob'
    url = 'url'

class Arguments(Types):
    slim = 'slim'
    overlay = 'overlay'
    margin = 'margin'
    upscale = 'upscale'


app = FastAPI()
app.mount("/public", StaticFiles(directory="public/"), name="public")
templates = Jinja2Templates(directory="public")
sk = Skindentity()


@app.get("/", response_class=HTMLResponse)
async def landing(request: Request):
    kwargs = {
        'request': request,
        'renders': RenderTypes.list(),
        'inputs': InputTypes.list(),
        'arguments': Arguments.list()
    }
    return templates.TemplateResponse("index.html", kwargs)

@app.get('/{render_type}/{input_type}/{input:path}')
async def get(
    render_type: RenderTypes,
    input_type: InputTypes,
    input: str,

    slim:    bool = Query(False, description="Whether the skin uses the slim body type."),
    overlay: bool = Query(True, description="Whether or not to show the skin's overlay layers."),
    margin:  int  = Query(0, description="How many pixels around the image to make transparent. (1 to 8)", ge=1, le=8),
    upscale: int  = Query(1, description="How many times to increase the size of a pixel. (2 to 8)", ge=2, le=8)
):
    args = [slim, overlay, margin, upscale]
    kwargs = {
        input_type.value: input,
        'renderer': render_type.value
    }
    print(args, kwargs)

    try:
        result = sk.render(*args, **kwargs)
    except Exception as exception:
        raise HTTPException(status_code=404, detail=str(exception))

    byte_result = BytesIO()
    result.save(byte_result, format='PNG')
    byte_result.seek(0)

    return StreamingResponse(byte_result, media_type="image/png")
