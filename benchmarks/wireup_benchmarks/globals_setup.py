import contextlib
from typing import Dict

import fastapi

from wireup_benchmarks import services
from wireup_benchmarks.services import (
    A,
    B,
    C,
    D,
    E,
    F,
    G,
    H,
    I,
    Plugin,
    PluginAlpha,
    PluginBlue,
    PluginGreen,
    PluginRed,
)

settings = services.Settings()
a = services.A(start=settings.start)
b = services.B(a=a)

_plugin_red = PluginRed()
_plugin_green = PluginGreen()
_plugin_blue = PluginBlue()
_plugin_alpha = PluginAlpha()
plugins_set: set[Plugin] = {_plugin_red, _plugin_green, _plugin_blue, _plugin_alpha}
plugins_map: dict[str, Plugin] = {
    "red": _plugin_red,
    "green": _plugin_green,
    "blue": _plugin_blue,
    "alpha": _plugin_alpha,
}

router = fastapi.APIRouter()


@router.get("/globals/singleton")
async def fastapi_singleton() -> Dict[str, str]:
    services.record_request("singleton")
    assert a.start == 10
    assert isinstance(a, A)
    assert isinstance(b, B)
    return {}


@router.get("/globals/scoped")
async def globals_scoped() -> Dict[str, str]:
    services.record_request("scoped")
    c = C()
    d = D(c=c)
    e = E(c=c, d=d)
    f = F(c=c, d=d, e=e)
    g = G(c=c, d=d, e=e, f=f)
    with contextlib.contextmanager(services.make_h)(c=c, d=d) as h:
        assert isinstance(h, H)
    async with contextlib.asynccontextmanager(services.make_i)(e=e, f=f) as i:
        assert isinstance(i, I)

    assert isinstance(c, C)
    assert isinstance(d, D)
    assert isinstance(e, E)
    assert isinstance(f, F)
    assert isinstance(g, G)
    assert isinstance(h, H)
    assert isinstance(i, I)
    return {}


@router.get("/globals/collection_set")
async def globals_collection_set() -> Dict[str, str]:
    services.record_request("collection_set")
    assert len(plugins_set) == 4
    return {}


@router.get("/globals/collection_map")
async def globals_collection_map() -> Dict[str, str]:
    services.record_request("collection_map")
    assert set(plugins_map.keys()) == {"red", "green", "blue", "alpha"}
    return {}
