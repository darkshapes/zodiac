# SPDX-License-Identifier: MPL-2.0 AND LicenseRef-Commons-Clause-License-Condition-1.0
# <!-- // /*  d a r k s h a p e s */ -->

from typing import Callable
import toga


class CommandPalette:
    async def ticker(self, widget: Callable, external: bool = False, **kwargs) -> toga.Widget:
        """Process and synthesize input data based on selected model.\n
        :param widget: The UI widget that triggered this action, typically used for state management.\n
        :type widget: toga.widgets
        :param external: Indicates whether the processing should be handled externally (e.g., via clipboard), defaults to False
        :type external: bool"""
        from zodiac.toga.signatures import ready_predictor

        self.response_panel.value += f"{os.path.basename(self.registry_entry.model)} :\n"

        await self.token_stream.set_tokenizer(self.registry_entry)
        prompts = {}
        if self.message_panel.value:
            cache = False
            prompts.setdefault("text", self.message_panel.value)
        stream = True if self.output_types.value == "text" else False
        # prompts.setdefault("audio",[0]) if else []
        # prompts.setdefault("image",[]) if image": []

        if stream:
            context_data, predictor_data = await ready_predictor(self.registry_entry, dspy_stream=stream, async_stream=stream, cache=cache)
            await self.stream_text(prompts, context_data, predictor_data)
        else:
            await self.generate_media(prompts, self.registry_entry)  # context_data, predictor_data)
        return widget

    async def stream_text(self, prompts, context_data, predictor_data):
        from zodiac.toga.signatures import Predictor
        from litellm.types.utils import ModelResponseStream  # StatusStreamingCallback
        from dspy.streaming import StatusMessage, StreamResponse

        self.response_panel.scroll_to_bottom()
        with dspy_context(**context_data):
            self.program = streamify(Predictor(), **predictor_data)
            async for prediction in self.program(question=prompts["text"]):
                if isinstance(prediction, ModelResponseStream) and prediction["choices"][0]["delta"]["content"]:
                    self.response_panel.value += prediction["choices"][0]["delta"]["content"]
                elif isinstance(prediction, StreamResponse) or hasattr(prediction, "chunk"):
                    self.response_panel.value += str(prediction.chunk)
                elif isinstance(prediction, Prediction) or hasattr(prediction, "answer"):
                    self.response_panel.value += str(prediction.answer)
                elif isinstance(prediction, StatusMessage) or hasattr(prediction, "message"):
                    self.status_display.text = self.status_text_prefix + str(prediction.message)
        self.response_panel.value += "\n--\n\n"
        return prediction

    async def generate_media(self, prompts, registry_entry) -> None:  # , predictor_data
        from nnll.tensor_pipe.construct_pipe import ConstructPipeline
        from nnll.tensor_pipe.inference import run_inference
        from zodiac.streams.class_stream import best_package
        from zodiac.providers.constants import MIR_DB

        pkg_data = await best_package(pkg_data=registry_entry)
        constructor = ConstructPipeline()
        pipe_data = constructor.create_pipeline(registry_entry, pkg_data, MIR_DB)
        return run_inference(pipe_data, prompts)

        # from zodiac.toga.signatures import Predictor

        # return prediction

    async def halt(self, widget, **kwargs) -> None:
        """Stop processing prompt\n
        :param widget: The calling widget object"""
        if not self.program.done():
            import gc

            del self.program
            gc.collect()
            self.status_display.text = self.status_text_prefix + "Cancelled."

    async def empty_prompt(self, widget, **kwargs) -> None:
        """Clears the prompt input area.
        :param widget: Triggering widget"""
        self.message_panel.value = ""

    async def copy_reply(self, widget, **kwargs) -> None:
        """Push the reply into the clipboard
        :param widget: Triggering widget"""
        import pyperclip

        pyperclip.copy(self.response_panel.value)
        self.status_display.text = self.status_text_prefix + self.status_info[7]

    async def attach_file(self, widget, **kwargs) -> None:
        """Attaches a file's contents to the prompt area.
        :param widget: Triggering widget"""
        import json

        try:
            file_path_named = await self.main_window.dialog(toga.OpenFileDialog(title="Attach a file to the prompt"))
            self.status_display.text = f"Read. {file_path_named}"
            if file_path_named is not None:
                from nnll.metadata.json_io import read_json_file

                file_contents = read_json_file(file_path_named)
                self.message_panel.scroll_to_bottom()
                self.message_panel.value = json.dumps(file_contents)
                self.status_display.text = self.status_text_prefix + self.status_info[6]
            else:
                self.status_display.text = self.status_text_prefix + self.status_info[4]
        except (ValueError, json.JSONDecodeError):
            self.status_display.text = self.status_text_prefix + self.status_info[5]

    async def reset_position(self, widget, **kwargs) -> None:
        """Scrolls text panel to bottom after content update.
        :param widget: text panel widget
        """
        setattr(self, "position_counter", getattr(self, "position_counter", 0) + 1)
        if max(self.scroll_buffer, self.position_counter) >= self.scroll_buffer:
            self.position_counter = 0
            widget.scroll_to_bottom()

    async def on_select_handler(self, widget, **kwargs) -> None:
        """React to input/output choice\n
        :param widget: The widget that triggered the event."""
        selection = widget.value
        if self.model_stream._graph.registry_entries is not None:
            self.registry_entry = next(iter(registry["entry"] for registry in self.model_stream._graph.registry_entries if selection in registry["entry"].model))
            await self.populate_task_stack()
            await self.token_stream.set_tokenizer(self.registry_entry)
        else:
            self.registry_entry = "No model..."

    async def model_graph(self):
        """Builds the model graph."""
        await self.model_stream.model_graph()

    async def populate_in_types(self) -> None:
        """Builds the input types selection."""
        in_edge_names = await self.model_stream.show_edges()
        self.input_types.items = in_edge_names

    async def populate_out_types(self) -> None:
        """Builds the output types selection."""
        out_edges = await self.model_stream.show_edges(target=True)
        self.output_types.items = out_edges

    async def populate_model_stack(self, widget: toga.Widget = None, **kwargs) -> None:
        """Builds the model stack selection dropdown."""

        await self.model_stream.clear()
        if self.input_types.value and self.output_types.value:
            models = await self.model_stream.trace_models(self.input_types.value, self.output_types.value)
            self.model_stack.items = models  # [model[0][:20] for model in models if len(model[0]) > 20]
            await self.token_estimate(widget=self.message_panel)

    async def populate_task_stack(self, widget: toga.Widget = None, **kwargs) -> None:
        """Builds the task stack selection dropdown."""
        selection = self.model_stack.value
        if self.model_stream._graph.registry_entries:
            registry_entry = next(
                iter(
                    registry["entry"]  # formatting
                    for registry in self.model_stream._graph.registry_entries  # formatting
                    if selection in registry["entry"].model
                )
            )
        else:
            registry_entry = "No models..."
        await self.task_stream.set_filter_type(self.input_types.value, self.output_types.value)
        if registry_entry and not isinstance(registry_entry, str):
            tasks = await self.task_stream.filter_tasks(registry_entry)
        else:
            tasks = ""

        self.task_stack.items = tasks

    async def switch_tabs(self, widget: toga.Widget = None, **kwargs) -> None:
        """Switches between text and graph tabs.
        :param widget: The triggering widget (optional), defaults to None"""
        self.browser_panel.evaluate_javascript("location.reload();")
        self.bg = self.bg_graph if self.bg == self.bg_text else self.bg_text
        self.final_layout.style.background_color = self.bg
        self.final_layout.refresh()
        self.status_display.text += self.status_info[0]
        await self.ping_server(widget=self.status_display)

    async def ping_server(self, widget: toga.Widget, **kwargs) -> toga.Widget:
        self.browser_panel.url = self.graph_server
        try:
            request = requests.get(self.graph_server, timeout=(3, 3))
            if request is not None:
                if hasattr(request, "status_code"):
                    status = request.status_code
                if (hasattr(request, "ok") and request.ok) or (hasattr(request, "reason") and request.reason == "OK"):
                    await self.active_server()
                elif hasattr(request, "json"):
                    status = request.json()
                    if status.get("result") == "OK":
                        await self.active_server()
                else:
                    self.browser_panel.url = self.graph_disabled
                    await self.active_server(False)
            else:
                self.browser_panel.url = self.graph_disabled
                await self.active_server(False)
        except (ConnectTimeout, ConnectionError, ConnectionRefusedError, MaxRetryError, NewConnectionError, OSError):
            await self.active_server(False)
            pass
        return widget

    async def active_server(self, enabled: bool = True):
        if not enabled:
            status_info = self.status_info[1]
            self.browser_panel.url = self.graph_disabled
        else:
            status_info = self.status_info[2]
            self.browser_panel.url = self.graph_server
        for info in self.status_info:
            self.status_display.text = self.status_display.text.replace(info, "")
        self.status_display.text += status_info
