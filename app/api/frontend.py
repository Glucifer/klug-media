from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.responses import Response
from starlette.types import Scope

router = APIRouter(tags=["frontend"])

WEB_ROOT = Path(__file__).resolve().parents[1] / "web"


class FrontendStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope: Scope) -> Response:
        response = await super().get_response(path, scope)
        response.headers["Cache-Control"] = "no-cache"
        return response


@router.get("/", include_in_schema=False)
def frontend_index() -> FileResponse:
    return FileResponse(
        WEB_ROOT / "index.html",
        headers={"Cache-Control": "no-cache"},
    )
