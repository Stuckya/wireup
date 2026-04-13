from typing import Any, Dict, List, Mapping

import fastapi
from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from typing_extensions import Annotated

from wireup_benchmarks import services
from wireup_benchmarks.services import Plugin, PluginAlpha, PluginBlue, PluginGreen, PluginRed


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=["wireup_benchmarks.dependency_injector_setup"])
    config = providers.Configuration()

    settings = providers.Singleton(services.Settings, start=config.start)
    a = providers.Singleton(services.make_a, settings=settings)
    b = providers.Singleton(services.B, a=a)
    c = providers.ContextLocalSingleton(services.C)
    d = providers.ContextLocalSingleton(services.D, c=c)
    e = providers.ContextLocalSingleton(services.E, c=c, d=d)
    f = providers.ContextLocalSingleton(services.F, c=c, d=d, e=e)
    g = providers.ContextLocalSingleton(services.G, c=c, d=d, e=e, f=f)
    # Context-local singletons to match per-request scoping without resource lifecycle.
    h = providers.ContextLocalSingleton(services.H, c=c, d=d)
    i = providers.ContextLocalSingleton(services.I, e=e, f=f)

    plugin_red = providers.Singleton(PluginRed)
    plugin_green = providers.Singleton(PluginGreen)
    plugin_blue = providers.Singleton(PluginBlue)
    plugin_alpha = providers.Singleton(PluginAlpha)
    plugins_list = providers.List(plugin_red, plugin_green, plugin_blue, plugin_alpha)
    plugins_map = providers.Dict(
        red=plugin_red,
        green=plugin_green,
        blue=plugin_blue,
        alpha=plugin_alpha,
    )


router = fastapi.APIRouter()


@router.get("/dependency_injector/singleton")
@inject
async def dependency_injector_singleton(
    a: Annotated[services.A, Depends(Provide[Container.a])],
    b: Annotated[services.B, Depends(Provide[Container.b])],
) -> Dict[str, Any]:
    services.record_request("singleton")
    assert a.start == 10
    assert isinstance(a, services.A)
    assert isinstance(b, services.B)
    return {}


@router.get("/dependency_injector/scoped")
@inject
async def dependency_injector_scoped(
    c: Annotated[services.C, Depends(Provide[Container.c])],
    cc: Annotated[services.C, Depends(Provide[Container.c])],
    ccc: Annotated[services.C, Depends(Provide[Container.c])],
    d: Annotated[services.D, Depends(Provide[Container.d])],
    dd: Annotated[services.D, Depends(Provide[Container.d])],
    e: Annotated[services.E, Depends(Provide[Container.e])],
    f: Annotated[services.F, Depends(Provide[Container.f])],
    g: Annotated[services.G, Depends(Provide[Container.g])],
    h: Annotated[services.H, Depends(Provide[Container.h])],
    i: Annotated[services.I, Depends(Provide[Container.i])],
) -> Dict[str, Any]:
    services.record_request("scoped")
    assert isinstance(c, services.C)
    assert c is cc
    assert cc is ccc

    assert isinstance(d, services.D)
    assert d is dd

    assert isinstance(e, services.E)
    assert isinstance(f, services.F)
    assert isinstance(g, services.G)
    assert isinstance(h, services.H)
    assert isinstance(i, services.I)

    return {}


@router.get("/dependency_injector/collection_set")
@inject
async def dependency_injector_collection_set(
    plugins: Annotated[List[Plugin], Depends(Provide[Container.plugins_list])],
) -> Dict[str, Any]:
    services.record_request("collection_set")
    assert len(plugins) == 4
    return {}


@router.get("/dependency_injector/collection_map")
@inject
async def dependency_injector_collection_map(
    plugins: Annotated[Mapping[str, Plugin], Depends(Provide[Container.plugins_map])],
) -> Dict[str, Any]:
    services.record_request("collection_map")
    assert set(plugins.keys()) == {"red", "green", "blue", "alpha"}
    return {}


container = Container()
container.config.from_dict({"start": 10})
container.wire(modules=[__name__])
