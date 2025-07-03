import asyncio
from zodiac.toga.app import ModelStream


async def test_show_edges():
    model_source = ModelStream()
    await model_source.model_graph()
    edge_data = None
    if hasattr(model_source, "int_proc") and model_source.int_proc.models is not None:
        edge_data = await model_source.show_edges()
    else:
        await asyncio.sleep(1)

    # source = await model_source.trace_models("text", "text")

    print(edge_data)
