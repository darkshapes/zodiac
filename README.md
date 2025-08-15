---
language:
- en
library_name: zodiac
license_name: MPL-2.0 + Commons Clause 1.0
---

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="img_src/zodiac_dark_stealth.png">
  <source media="(prefers-color-scheme: light)" srcset="img_src/zodiac_light_stealth.png">
  <img alt="Futuristic, slanted wireframe block type spelling the word 'ZODIAC' using overlapping and interweaving shapes and triangles for the 'O' and 'A'." src="img_src/zodiac_dark_bg.png">
</picture><br><br>


# zodiac <br><sub>self-arranging workflow automator</sub>

<div align="center">

### [ [Windows](https://github.com/darkshapes/sdbx/wiki/Develop) | [MacOS](https://github.com/darkshapes/sdbx/wiki/Develop) | [Linux](https://github.com/darkshapes/sdbx/wiki/Develop) ]

![A dark theme screenshot of the image](img_src/screenshot07-14.png)
 <hr>
 </div>
Zodiac is a creative research platform for Generative AI. Guided by text, audio, or files, it identifies your models (text, image, speech, video, anything) and constructs generative AI workflows, eliminating the need for technical expertise in building action chains. It empowers users to focus on creating art, storytelling, research, and tool development, rather than the mechanics of creation, enabling exploration of emerging technology on virtually any system immediately, rather than after months of study.

> [!NOTE]
> Zodiac runs **locally** and **only** on your devices. Outside connections are not opened. Read the code & see for yourself.

* Sequence an infinite variety of generative workflows with ease
* No programming necessary
* Minimal, lightweight and versatile: Designed for smartphone, CLI terminal and browser use
* Local-first, privacy-oriented isolation: no data siphoning, remote telemetry or analytics
* Compatible with legacy consumer computer/CPU/TPU/GPU devices,
* Bring your own models - Supports [Ollama](https://ollama.com/), [Llamafile](http://github.com/Mozilla-Ocho/llamafile), [Cortex/Jan](http://cortex.so), [VLLM](https://github.com/vllm-project/vllm), [LMStudio](http://lmstudio.ai/), [HuggingFace](https://huggingface.co/)
* Support expanding to include: , CivitAI, ModelScope & AIO (all-in-one) local caches through [sdbx](https://github.com/darkshapes/sdbx).<br><br>


[![Python application test status](https://github.com/darkshapes/zodiac/actions/workflows/zodiac.yml/badge.svg)](https://github.com/darkshapes/zodiac/actions/workflows/zodiac.yml) <br>
![commits per month](https://img.shields.io/github/commit-activity/m/darkshapes/zodiac?color=indigo)<br>
![code size](https://img.shields.io/github/languages/code-size/darkshapes/zodiac?color=navy)<br>
[<img src="https://img.shields.io/discord/1266757128249675867?color=5865F2">](https://discord.gg/VVn9Ku74Dk)<br>
[<img src="https://img.shields.io/badge/me-__?logo=kofi&logoColor=white&logoSize=auto&label=feed&labelColor=maroon&color=grey&link=https%3A%2F%2Fko-fi.com%2Fdarkshapes">](https://ko-fi.com/darkshapes)<br>
<br>


## Quick Guide


### Install

Install [uv](https://github.com/astral-sh/uv#installation), then run these terminal commands
- >
  >```
  > git clone https://github.com/darkshapes/zodiac
  > cd zodiac
  > uv sync --group dev
  > ```

### Use

Enter a terminal and activate the python environment in
- >
  > Linux/Macos:
  > ```
  > source .venv/bin/activate
  > ```

  > Windows Powershell:
  > ```
  > Set-ExecutionPolicy Bypass -Scope Process -Force; .venv\Scripts\Activate.ps1
  > ```

> [!IMPORTANT]
> ## Classes, Methods & Constants :
> ```
> RegistryEntry
>            `---------------------------Local model registry class, collects and identifies
> IntentProcessor
>              `-------------------------Graph of local models and execution estimator
> ModelStream/TaskStream/TokenStream
>                                 `------Feed methods for interface operation
> CueType/PkgType/ChipType Constants
>                                  `-----Enumuerations of available hardware, services, and dependencies
> Signatures
>         `------------------------------DSPY signatures, custom routines for models
> Interface
>        `-------------------------------Toga GUI components
> ```
> ##  Available terminal commands:<br>
> Launch program with<br>
> - `zdac`<br>
> - or<br>
> - `zodiac`

### [Detailed instructions :](https://github.com/darkshapes/sdbx/wiki/Develop)

Discussion topics, issue requests, reviews, and code updates are encouraged. Build with us! Talk to us in [our Discord](https://discord.gg/VVn9Ku74Dk)!

</div>



