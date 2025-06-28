import asyncio
from zodiac.toga.app import ModelSource


async def test_show_edges():
    model_source = ModelSource()
    await model_source.build_graph()
    if hasattr(model_source, "int_proc"):
        edge_data = await model_source.show_edges()
    else:
        asyncio.wait(1)
    print(edge_data)
