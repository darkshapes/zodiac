
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="img_src/zodiac_dark_stealth.png">
  <source media="(prefers-color-scheme: light)" srcset="img_src/zodiac_light_stealth.png">
  <img alt="Fallback image description" src="img_src/zodiac_dark_bg.png">
</picture>

# Zodiac

Zodiac is a creative tool for DIY Generative AI. Guided by text, audio, or copied/pasted files, Zodiac easily chains sophisticated model systems together so that you can concentrate on making the art you want to make, the story you want to tell, and the tools you want to build, rather than build the tool to begin with.

> [!NOTE]
> Zodiac runs locally and only on your device. Outside connections are disabled by default. Read the code & see for yourself.


We currently support popular repositories like Ollama and LMStudio, VLLM, and will support models from HuggingFace, CivitAI, and ModelScope, and standards like llamafile and MLX through [sdbx](https://github.com/darkshapes/sdbx).

More details forthcoming.

![commits per month](https://img.shields.io/github/commit-activity/m/darkshapes/zodiac?color=indigo)<br>
![code size](https://img.shields.io/github/languages/code-size/darkshapes/zodiac?color=navy)<br>
![Discord](https://img.shields.io/discord/1266757128249675867?color=black)<br><br>

## Installing

> [!IMPORTANT]
> Please note Zodiac is in a very incomplete demonstration state at the moment. Read <A href="#contributing">contributing</a>.

To install Zodiac you can use [`uv`](https://github.com/astral-sh/uv#installation):

```
uv pip install git+https://github.com/darkshapes/zodiac
```
or
<details ><summary>pip </summary>

> **1** : clone repo
>
> ```
> git clone https://github.com/darkshapes/zodiac.git
> ```

> **2** : Make a virtual environment
> ```
> python -m venv .venv
> ```

> **3** : Activate environment
> <details ><summary>Windows</summary>
>
> **(powershell):**
> ```
> Set-ExecutionPolicy Bypass -Scope Process -Force; .venv\Scripts\Activate.ps1
>
> ```
>
> **(cmd):**
> ```
> .venv\Scripts\activate.bat
> ```
>
> </details><br>
>
> <details ><summary>Linux/MacOS</summary>
>
> ```
> source .venv/bin/activate
> ```
>
>  </details>
<br>

> **4** : Install
> ```
> pip install zodiac
> ```

</details><br>


Once installed, the terminal client can be launched with its command:
```
zodiac
```

Or, you can run the client in a local browser:
```
textual serve zodiac
```

> [!TIP]
> You can also try Zodiac from command line without any installation using [`uv`](https://github.com/astral-sh/uv#installation):
> ```
> uvx --from git+https://github.com/darkshapes/zodiac zodiac
> ```

## Contributing

We have a lot of plans so, feel free to talk to us in discussion, issues or in the <A href="discord.gg/RYaJw9mPPe">darkshapes discord server</a>

* Environment  : uv
* Testing      : pytest -vv tests/*.py
* Formatting   : ruff/better align
* Linting      : ruff/pylint
* Type Checking: pylance/pyright
* Spelling     : typos vsc
* Docstrings   : sphinx


