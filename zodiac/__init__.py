#  # # <!-- // /*  SPDX-License-Identifier: MPL-2.0  */ -->
#  # # <!-- // /*  d a r k s h a p e s */ -->

import sys
import os
import argparse
import multiprocessing as mp

mp.set_start_method("spawn", force=True)
sys.path.append(os.getcwd())
# import platform

# if platform.system == "darwin":
#     import multiprocessing as mp

#     mp.set_start_method("fork", force=True)


def start_trace():
    from viztracer import VizTracer
    from datetime import datetime

    assembled_path = os.path.join("log", f".nnll{datetime.now().strftime('%Y%m%d')}_trace.json")
    os.makedirs("log", exist_ok=True)
    tracer = VizTracer()
    tracer.start()
    return tracer, assembled_path


def set_env(args: argparse.ArgumentParser):
    os.environ["TELEMETRY"] = "False"
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    try:
        import huggingface_hub
    except (ImportError, ModuleNotFoundError, Exception):  # pylint: disable=broad-exception-caught
        pass
    else:
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
        # huggingface_hub.constants.HF_HUB_VERBOSITY

    try:
        import litellm
    except (ImportError, ModuleNotFoundError, Exception):  # pylint: disable=broad-exception-caught
        pass
    else:
        litellm.disable_token_counter = False
        litellm.disable_streaming_logging = True
        litellm.turn_off_message_logging = True
        litellm.suppress_debug_info = False
        litellm.json_logs = False  # type: ignore
        litellm.disable_end_user_cost_tracking = True
        litellm.telemetry = False
        litellm.disable_hf_tokenizer_download = not args.net  # -net = True -> disable download = False/0
        os.environ["DISABLE_END_USER_COST_TRACKING"] = "True"
    return True


def main() -> None:
    """Parse launch arguments (mostly turning down/disconnecting loud dependency packages)\n
    :param args: Launch arguments from command line
    """

    parser = argparse.ArgumentParser(description="Multimodal generative media sequencer")
    parser.add_argument("-n", "--net", action="store_true", help="Allow network access (for downloading requirements)")
    parser.add_argument("-t", "--trace", action="store_true", help="Enable trace logs (generated in log folder)")

    parser.add_argument("-d", "--diag", action="store_true", help="Process using diagnostic settings")

    args = parser.parse_args()

    parser = argparse.ArgumentParser(description="Multimodal generative media sequencer")
    parser.add_argument("-n", "--net", action="store_true", help="Allow network access (for downloading requirements)")
    parser.add_argument("-t", "--trace", action="store_true", help="Enable trace logs (generated in log folder)")

    parser.add_argument("-d", "--diag", action="store_true", help="Process using diagnostic settings")

    args = parser.parse_args()

    env_ready = set_env(args)
    if env_ready:
        tracer, assembled_path = start_trace() if args.trace else None, None
        return tracer, assembled_path


if __name__ == "__main__":
    tracer, assembled_path = main()
    if tracer and hasattr(tracer.stop):
        tracer.stop()
        tracer.save(output_file=assembled_path)
