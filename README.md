# Unofficial Pygame Community Pass-the-code Game Jam 2025
There are two teams, each creating a game. Only one person from each team works at the team's project in a given moment. Each participant has as week to work on the project. After that time is up, it's the turn for the next person. Commit to the repository regularly to avoid code loss (in your time frame).

Team one Commit Crimes (times are in UTC):
1) @David Ward Monday, February 17, 2025 at 12:00 AM - Monday, February 24, 2025 at 12:00 AM
2) @Matiiss Monday, February 24, 2025 at 12:00 AM - Monday, March 3, 2025 at 12:00 AM
3) @farkas15 Monday, March 3, 2025 at 12:00 AM - Monday, March 10, 2025 at 12:00 AM
4) @Dusty Monday, March 10, 2025 at 12:00 AM - Sunday, March 17, 2025 at 12:00 AM
5) @Axis Monday, March 17, 2025 at 12:00 AM - Monday, March 24, 2025 at 12:00 AM
6) @Dolfino Monday, March 24, 2025 at 12:00 AM - Monday, March 31, 2025 at 12:00 AM

## Rules
Rules in use are a modified version of those for https://itch.io/jam/pygame-community-fall-jam-2024

- Pre-existing engine/utility code can be reused for this jam. However, code specific for this jam must be created after the jam starts.
- Pygame(-ce) must be the primary tool used for rendering and sound. Using things such as, e.g. modernGL for shaders or pyaudio for sound manipulation is allowed, but pygame must be used for the bulk of the work. This helps to keep things even between participants. (If possible, the pygame-ce fork of pygame should be used).
- You MUST create all assets used in your entry during the jam. Asset generators are perfectly fine to use, but NO premade assets are allowed, even if you have the rights to them. This includes creative commons works (even CC0). Exceptions:
- Things in the public domain that are over ~70 years old (e.g. classical music pieces, old paintings, etc)
- Fonts (which you must, of course, still have license to use).
- Premade splash screens or logos
- Pygame assets from https://pyga.me/docs/logos.html exclusively.
- Please be careful with delicate or controversial subject matter. Do not make games with NSFW/18+ content. If you are unsure whether you can include something in your entry, ask a member of staff on the Discord server.
- Follow the spirit of pass-the-code challenge: the communication regarding the development of the submission should only happen through the code that is implemented. Each participant has the freedom of interpreting by themselves what's the game that is created.
- The winning submission will be determined by a popularity vote determined by a number of stars that a given submission got in the submission channel (reactions by participants don't count).
- The last member of a team is also tasked with creating a submission on #showcase-submissions within their time-frame (this includes "marketing materials", like showcase videos).
- You are not allowed to have fun throughout the creation process. Any team caught enjoying the jam will be disqualified! /s

## Development setup

### Package manager
It is strongly recommended* to use `uv` as the package manager. To install it:
- On UNIX systems:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- On Windows:
  ```ps
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```
For a more thorough guide, consult the official documentation: https://docs.astral.sh/uv/getting-started/installation/  
<sub>* - following instructions will mostly make use of `uv`'s interfaces, though of course one doesn't HAVE to use it</sub>

### Install all dependencies in a virtual environment at the root of the project
On Windows, you'd likely use `.venv/source` instead of `.venv/bin`

With `uv`:
```bash
uv venv .venv
uv pip install --editable .[dev]
```
With `pip`:
```bash
python -m venv .venv
.venv/bin/python -m pip install --editable .[dev]
```

### Activate your virtual environment
```bash
source .venv/bin/activate
```

### Setting up pre-commit hooks
```bash
uvx pre-commit install
```
If you make edits or pull in new changes from the remote, it's a good idea to run this just in case
someone has updated the config.

### Running the game
Make sure you have activated the virtual environment and simply run this:
```bash
python main.py
```

### Running the game (VS Code)
You can simply press F5 (or whatever key you have remapped that action to) and it should launch the game
