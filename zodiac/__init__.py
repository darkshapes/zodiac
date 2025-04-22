import sys
import os

# pylint:disable=import-outside-toplevel
sys.path.append(os.getcwd())


def main() -> None:
    """Launch textual UI"""
    from zodiac.__main__ import Combo
    from nnll_01 import info_message as nfo

    trace = False
    if sys.argv[0] == "-t" or sys.argv[0] == "--trace":
        import litellm
        from viztracer import VizTracer

        litellm.suppress_debug_info = False
        trace = True
        tracer = VizTracer()
        tracer.start()

    app = Combo(ansi_color=False)

    nfo("Launching...")
    app.run()
    if trace:
        from datetime import datetime

        os.makedirs("log", exist_ok=True)
        assembled_path = os.path.join("log", f".nnll{datetime.now().strftime('%Y%m%d')}_trace.json")
        tracer.stop()
        tracer.save(output_file=assembled_path)  # also takes output_file as an optional argument


if __name__ == "__main__":
    # import asyncio
    main()
    # asyncio.run(main())
