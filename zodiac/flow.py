# from nnll_15 import RegistryEntry, from_cache
# from nnll_01 import dbug

# from dspy import Module as dspy_Module
# import networkx as nx


# # from nnll_11 import BasicImageSignature
# # from nnll_15.constants import LibType
# # import asyncio
# # from nnll_01 import nfo, dbug
# # from zodiac.__main__ import Combo
# # from nnll_05 import lookup_function_for
# # from nnll_64 import run_inference

# from zodiac.graph import IntentProcessor

# graph = IntentProcessor()
# graph.calc_graph()
# graph.set_path(mode_in=mode_in, mode_out=mode_out)
# graph.set_ckpts()
# graph.ckpts

# class FlowBuilder:
#     def __init__(self, graph: nx.Graph, first_in: str = "text", last_out: str = "text", initial_tx: dict = None) -> None:
#         self.graph = graph
#         self.first_in = first_in
#         self.last_out = last_out
#         self.tx_data: dict = None

#     def ready_tx(
#         self,
#         mode_in: str,
#         mode_out: str,
#     ) -> dict:

#     def walk_intent(self, bypass_send=True) -> None:
#         """Provided the coordinates in the intent processor, follow the list of in and out methods\n
#         :param bypass_send: Find intent path, but do not process, defaults to True
#         """

#         tx_data = self.ready_tx(mode_in)
#         coords = self.graph.coord_path
#         hops = len(coords) - 1
#         for i in range(hops):
#             if i + 1 < hops:
#                 if not bypass_send:
#                     self.send_tx(tx_data, last_hop=False)
#                     tx_data = self.ready_tx(mode_in=coords[i + 1], mode_out=coords[i + 2])
#                 else:  # This allows us to predict the models required for a pass
#                     old_models = self.graph.models if self.graph.models else []
#                     dbug("walk_intent", old_models)
#                     self.ready_tx(mode_in=coords[i + 1], mode_out=coords[i + 2])
#                     self.graph.models.extend(old_models)
#                     dbug(self.graph.models)

#             elif not bypass_send:
#                 self.send_tx(tx_data)

#     async def synthesize(self, chat: dspy_Module, chat_args: dict, streaming=True) -> dict | None:
#         from litellm import ModelResponseStream
#         from dspy import Prediction

#         async for tick in chat.forward(streaming=streaming, **chat_args):
#             try:
#                 async for chunk in tick:
#                     if isinstance(chunk, Prediction) and streaming:
#                         if hasattr(chunk, "answer") and chunk.answer not in self.text:
#                             """insert(c.answer)"""
#                         # reset color
#                     elif isinstance(chunk, ModelResponseStream):
#                         """insert(chunk["choices"][0]["delta"]["content"] if chunk["choices"][0]["delta"]["content"] is not None else " ")"""
#             except (GeneratorExit, RuntimeError) as error_log:
#                 dbug(error_log)

#     def send_tx(ckpt, tx_data, last_hop=True):
#         # prepare text area \n---\n"
#         # start indicator
#         from nnll_05 import lookup_function_for

#         ckpt = next(iter(self.graph.ckpts)).get("entry") if ckpt is None else ckpt
#         from nnll_11 import QASignature, BasicImageSignature

#         sig = QASignature
#         if mode_out == "image":
#             sig = BasicImageSignature
#             constructor, mir_arch = lookup_function_for(ckpt.model)
#             constructor(mir_arch)
#         else:
#             from nnll_11 import ChatMachineWithMemory

#             chat_args = {
#                 "tx_data": tx_data,
#                 "model": ckpt.model,
#                 "library": ckpt.library,
#             }
#             stream = mode_out == "text"
#             chat = ChatMachineWithMemory(sig=sig, max_workers=8, stream=stream)
#             try:  # and this
#                 synthesize(chat=chat, chat_args=chat_args, streaming=stream)
#             except (GeneratorExit, RuntimeError) as error_log:
#                 dbug(error_log)
#                 # return indicator state
