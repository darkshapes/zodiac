import asyncio
from zodiac.toga.app import ModelSource


async def test_show_edges():
    model_source = ModelSource()
    await model_source.model_graph()
    edge_data = None
    if hasattr(model_source, "int_proc"):
        edge_data = await model_source.show_edges()
    else:
        await asyncio.sleep(1)
    source = await model_source.trace_models("text", "text")
    print(edge_data)
