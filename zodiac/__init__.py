#  # # <!-- // /*  SPDX-License-Identifier: MPL-2.0  */ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

import multiprocessing as mp

mp.set_start_method("spawn", force=True)


import sys
import os
from nnll.configure import HOME_FOLDER_PATH

# pylint:disable=import-outside-toplevel
sys.path.append(os.getcwd())


def set_env(args: bool) -> None:
    """Parse launch arguments (mostly turning down/disconnecting loud dependency packages)\n
    :param args: Launch arguments from command line
    """

    os.environ["TELEMETRY"] = "False"

    try:
        import huggingface_hub

        huggingface_hub.constants.HF_HUB_DISABLE_TELEMETRY = 1  # privacy
        huggingface_hub.constants.HF_HUB_DISABLE_IMPLICIT_TOKEN = 1
        huggingface_hub.constants.HF_XET_HIGH_PERFORMANCE = int(args.net or args.diag)  # download methods (if online)
        huggingface_hub.constants.HF_HUB_ENABLE_HF_TRANSFER = int(args.net or args.diag)
        huggingface_hub.constants.HF_HUB_DISABLE_PROGRESS_BARS = int(not args.diag)  # superficial/diagnostic
        huggingface_hub.constants.HF_HUB_OFFLINE = int(not args.net or not args.diag)  # -net = True -> hub offline = False/0
        os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
        os.environ["HF_HUB_DISABLE_IMPLICIT_TOKEN"] = "1"
        os.environ["HF_XET_HIGH_PERFORMANCE"] = str(int(args.net or args.diag))
        os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = str(int(args.net or args.diag))
        os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = str(not args.diag)
        os.environ["HF_HUB_OFFLINE"] = str(int(not args.net or not args.diag))

        os.environ["DISABLE_HF_TOKENIZER_DOWNLOAD"] = str(not args.net or not args.diag)  # litellm

    except (ImportError, ModuleNotFoundError, Exception):  # pylint: disable=broad-exception-caught
        pass

    try:
        import litellm

        litellm.disable_streaming_logging = True
        litellm.turn_off_message_logging = True
        litellm.suppress_debug_info = True
        litellm.json_logs = True  # type: ignore

        litellm.disable_end_user_cost_tracking = True
        litellm.telemetry = False
        litellm.disable_hf_tokenizer_download = not args.net  # -net = True -> disable download = False/0
        os.environ["DISABLE_END_USER_COST_TRACKING"] = "True"

        # huggingface_hub.constants.HF_HUB_VERBOSITY

    except (ImportError, ModuleNotFoundError, Exception):  # pylint: disable=broad-exception-caught
        pass

    USER_PATH_NAMED = os.path.join(HOME_FOLDER_PATH, "config.toml")


def main() -> None:
    """Launch textual UI"""
    # import platform

    # if platform.system == "darwin":
    #     import multiprocessing as mp

    #     mp.set_start_method("fork", force=True)

    import argparse
    from zodiac.__main__ import Combo
    from nnll.monitor.file import nfo

    parser = argparse.ArgumentParser(description="Multimodal generative media sequencer")
    parser.add_argument("-n", "--net", action="store_true", help="Allow network access (for downloading requirements)")
    parser.add_argument("-t", "--trace", action="store_true", help="Enable trace logs (generated in log folder)")

    parser.add_argument("-d", "--diag", action="store_true", help="Process using diagnostic settings")

    args = parser.parse_args()

    set_env(args)

    if args.trace:
        from viztracer import VizTracer

        tracer = VizTracer()
        tracer.start()
    app = Combo(ansi_color=False)
    nfo("Launching...")
    app.run()
    if args.trace:
        from datetime import datetime

        os.makedirs("log", exist_ok=True)
        assembled_path = os.path.join("log", f".nnll{datetime.now().strftime('%Y%m%d')}_trace.json")
        tracer.stop()
        tracer.save(output_file=assembled_path)  # also takes output_file as an optional argument


if __name__ == "__main__":
    main()

    # asyncio.run(main()) #ValueError: a coroutine was expected, got None
    # RuntimeError: asyncio.run() cannot be called from a running event loop
