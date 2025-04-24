
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="img_src/zodiac_dark_stealth.png">
  <source media="(prefers-color-scheme: light)" srcset="img_src/zodiac_light_stealth.png">
  <img alt="Futuristic, slanted wireframe block type spelling the word 'ZODIAC' using overlapping and interweaving shapes and triangles for the 'O' and 'A'." src="img_src/zodiac_dark_bg.png">
</picture><br><br>

# zodiac <br><sub>multimodal generative media sequencer</sub>
<div align="center">

### [ [Windows](#installing) | [MacOS](#installing) | [Linux](#installing) ]

 <hr>
 </div>
Zodiac is a creative tool for DIY Generative AI. Guided by text, audio, or copied/pasted files, Zodiac easily chains sophisticated model systems together so that you can concentrate on making the art you want to make, the story you want to tell, and the tools you want to build, rather than build the tool to start making.

> [!NOTE]
> Zodiac runs **locally** and **only** on your device. Outside connections are not opened. Read the code & see for yourself.

We currently support popular repositories like  and will support models from HuggingFace, CivitAI, and ModelScope, and standards like llamafile and MLX through [sdbx](https://github.com/darkshapes/sdbx).

* Zodiac generates sophisticated multimodal, multi-model workflows
* Supports [Ollama](https://ollama.com/), [LMStudio](http://lmstudio.ai/), [Cortex](http://cortex.so), [Llamafile](http://github.com/Mozilla-Ocho/llamafile)
* Minimal and versatile operation in terminal console or browser
* Designed for consumer-grade hardware
* Local-first, privacy-oriented
* Sequences of specialized models lowers compute/emissions, increases adaptability/modularity. <br><br>

![commits per month](https://img.shields.io/github/commit-activity/m/darkshapes/zodiac?color=indigo)<br>
![code size](https://img.shields.io/github/languages/code-size/darkshapes/zodiac?color=navy)<br>
![Discord](https://img.shields.io/discord/1266757128249675867?color=black)<br><br>

## Installing <br>

> **1** : python
>
> Zodiac requires Python 3.10 or higher.
> You can install Python with [`uv`](https://github.com/astral-sh/uv#installation)
> ```
> uv python install 3.12`
> ```
> or [download from python.org](https://www.python.org/downloads/)

<br><br>
> **2** : download source
>
> To install Zodiac you can use [`uv`](https://github.com/astral-sh/uv#installation):
> ```
> uv pip install git+https://github.com/darkshapes/zodiac
> ```
> or
> <details ><summary>pip </summary>
>
>> **a**
>> ```
>> git clone https://github.com/darkshapes/zodiac.git
>> ```
>
>> **b** : Make a virtual environment
>> ```
>> python -m venv .venv
>> ```
>
>> **c** : Activate environment
>> <details ><summary>Windows</summary>
>>
>>> **(powershell):**
>>> ```
>>> Set-ExecutionPolicy Bypass -Scope Process -Force; .venv\Scripts\Activate.ps1
>>>
>>> ```
>>>
>>> **(cmd):**
>>> ```
>>> .venv\Scripts\activate.bat
>>> ```
>>>
>> </details><br>
>>
>> <details ><summary>Linux/MacOS</summary>
>>
>>> ```
>>> source .venv/bin/activate
>>> ```
>>>
>>  </details>

<br><br>
> **3** : build
>```
> uv pip install zodiac
> ```
> or
> ```
> pip install zodiac
> ```

</details><br>


Once installed use this command for terminal client:
```
zodiac
```

Or run the client in a local browser:
```
textual serve zodiac
```

Furthermore, the interface is designed to work on a mobile device using this `serve` command.
An independent session can be opened with the method from the same Wi-Fi network using browser or SSH.


> [!TIP]
> You can also try Zodiac from command line without any installation using [`uv`](https://github.com/astral-sh/uv#installation):
> ```
> uvx --from git+https://github.com/darkshapes/zodiac zodiac
> ```

> [!CAUTION]
> Be aware that even though Zodiac is local first, huggingface/ollama/vllm/operating system may not be set up this way. Zodiac changes the options in Python, but you can also change environment settings to ensure that you are only using cached data before the program launches:
>
> <details ><summary>Linux/MacOS</summary>
>
> ```
> export HF_HUB_DISABLE_TELEMETRY=1
> export export HF_HUB_OFFLINE=1
> ```
>  </details>
>
> <details ><summary>Windows</summary>
>
> ```
> set HF_HUB_DISABLE_TELEMETRY=1
> set export HF_HUB_OFFLINE=1
> ```
>  </details>

## Using

> [!IMPORTANT]
> Please note Zodiac is in a very incomplete demonstration state. Generating from speech recording, image generation, and full support for clipboard copying are not yet implemented, only the process of evaluating paths for models, text generation, and pasting in and out of console. Please check in with us as we continue to grow, or read about <A href="#contributing">contributing</a>.

<img alt="A screenshot of two grey text fields. At the top, someone has entered 'What is crystalline intelligence vs liquid intelligence?' The bottom shows a reply stating 'Crystalline intelligence refers to traditional, rule-based knowledge acquisition and application. It's like a well-structured database where information is stored in a rigid format, similar to a crystal lattice. This type of intelligence excels in well-defined tasks with clear rules, such as chess or trivia games.
Liquid intelligence, on the other hand, represents adaptability and the ability to navigate uncertainty. It's dynamic and flexible, much like liquid, allowing individuals to thrive in novel situations requiring creativity, problem-solving, and social skills. This form of intelligence is increasingly valuable in our rapidly changing world where many tasks don't have straightforward solutions. Both forms of intelligence are important and serve different purposes, reflecting the evolving nature of human cognition and the diverse demands of modern life.'" src="img_src/screenshot.png">

To use Zodiac, type into the top field, then adjust top and bottom input and output settings on the left. Left click or press tab key to focus out of top field, then tap **\`** (grave accent) to send your message along. To clear the log or any received input, hold shift and tap `backspace`. If you want to pick specific models, the box on the right lists available models that convert selected input to output. You can choose a model to add or remove it in the preferred list, indicated by the `*`.

### Keyboard Reference:
```
        Tab          : Switch Focus
Up/Down Arrow        : Change option
        Enter        : Begin recording audio
        Space        : Playback audio
        Ctrl-Z       : Undo
        Ctrl-Shift-Z : Redo
        ALT-Backspace: Clear input
        ESC          : Cancel Generation
        ESC/Ctrl-Qx2 : Quit
        Ctrl-C       : Copy (only in console mode)
        Ctrl-V/⌘-V   : Paste (only in console mode)
        Ctrl-X       : Cut (only in console mode)
```

## Contributing

### Technical Details

Zodiac works by graphing available local model services, then pathing a route through the graph to complete the user request. The system relies heavily on the [Textual](https://github.com/Textualize/textual), [dspy](https://github.com/stanfordnlp/dspy), and [networkx](https://github.com/networkx/networkx) libraries.

Currently we support models hosted using:
- [Ollama](https://ollama.com/)
- [LMStudio](http://lmstudio.ai/)
- [Cortex](http://cortex.so)
- [Llamafile](http://github.com/Mozilla-Ocho/llamafile)

Support is being considered for:
[TensorBlock](https://github.com/TensorBlock/TensorBlock-Studio) and [VLLM](https://github.com/vllm-project/vllm) (Compile-only for cpu).

Support is planned for:
- STS/TTS/Image/Video/LoRA models and MLX from Huggingface/CivitAI/ModelScope using <a href="https://github.com/darkshapes/sdbx">sdbx</a>
- Model recognition for non-diffusers standards using <a href="https://github.com/darkshapes/nnll">nnll</a>
- No-code node-graph workflow modification using <a href="https://github.com/darkshapes/singularity">Singularity</a>

As mentioned above, the system can be served to a mobile device on the LAN (textual serve). Because the interface runs in terminal console, Zodiac can also be run completely headless.

This unity completes the scope of <a href="https://github.com/darkshapes/>darkshapes</a> projects. Discussion topics, issue requests, reviews, and code updates are encouraged. Talk to us in our <A href="https://discord.gg/RYaJw9mPPe">Discord</a> to catch up-to-date information.

### Development Reference
```
*  Environment   : uv
   Telemetry     : False
HFHub Cache Only : True
*  Logging       : structlog (viztrace on crashes) to `/log` folder
*  Testing       : pytest -vv tests
*  Formatting    : ruff/better align
*  Linting       : ruff/pylint
*  Type Checking : pylance/pyright
*  Spelling      : typos vsc
*  Docstrings    : sphinx
*  CLI Commands  :

zodiac  [-h] [-n] [-t]            = Run Zodiac in the current terminal window
  -h, --help   show this help message and exit
  -n, --net    Allow network access (for downloading requirements)
  -t, --trace  Enable full tracelogging
textual     console [-x EVENTS]  = Run a live console logging session (use before textual --devzodiac/textual serve --dev)
textual     serve [--dev] zodiac = Host a localmachine server (shows CSS edits live, Python edits on refresh)
textual     run --dev zodiac     = Run an instance in command prompt using dev options (shows CSS edits live, relaunch for Python edits)
```

## Linking

<div align='center'>

![Image of the darkshapes 'neuron' logo, the letters DS with a superimposed illustration of a brain cell-type structure on top](https://cdn-avatars.huggingface.co/v1/production/uploads/65ff1816871b36bf84fc3c37/JZLA1RQXQ7NanLF5G9c6Q.png)

 darkshapes [ <A href="https://github.com/darkshapes">GitHub</a> ] [ <A href="https://discord.gg/RYaJw9mPPe">Discord</a> ] [ <A href="https://huggingface.co/darkshapes">HuggingFace</a> ] [ <A href="https://github.com/maxtretikov">MaxTretikov</a> ] [ <A href="https://github.com/exdysa">EXDYSA</a> ]
</div>



