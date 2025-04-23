import sys
import os

# pylint:disable=import-outside-toplevel
sys.path.append(os.getcwd())


def set_env(args: bool) -> None:
    import litellm

    litellm.disable_end_user_cost_tracking = True
    litellm.telemetry = False

    litellm.disable_hf_tokenizer_download = args.net

    try:
        import huggingface_hub

        huggingface_hub.constants.HF_HUB_DISABLE_PROGRESS_BARS = True
        huggingface_hub.constants.HF_HUB_DISABLE_TELEMETRY = True
        huggingface_hub.constants.HF_XET_HIGH_PERFORMANCE = True
        huggingface_hub.constants.HF_HUB_ENABLE_HF_TRANSFER = True
        huggingface_hub.constants.HF_HUB_DISABLE_IMPLICIT_TOKEN = True

        huggingface_hub.constants.HF_HUB_OFFLINE = not args.net

    except (ImportError, ModuleNotFoundError, Exception):  # pylint: disable=broad-exception-caught
        pass


def main() -> None:
    """Launch textual UI"""
    import argparse

    from zodiac.__main__ import Combo
    from nnll_01 import info_message as nfo

    parser = argparse.ArgumentParser(description="Multimodal generative media sequencer")
    parser.add_argument("-n", "--net", action="store_true", help="Allow network access (for downloading requirements)")
    parser.add_argument("-t", "--trace", action="store_true", help="Enable trace logs (generated in log folder)")

    args = parser.parse_args()

    set_env(args)

    if args.trace:
        import litellm
        from viztracer import VizTracer

        litellm.suppress_debug_info = False
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
    # import asyncio
    main()
    # asyncio.run(main())
