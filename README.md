# XAtlas GUI Wrapper
This is a wrapper around the unoffical python binding of XAtlas (https://github.com/jpcy/xatlas). It has a GUI you can use to unwrap and uv pack objs, and a CLI support for calling the .exe with command arguments (mesh input/ output etc). 

The project is using UV, best would be to use it as well for ease of setup. Look at Releases for a windows .exe release.

Technical Info:

A PySide6 GUI and silent command-line wrapper around the `xatlas` Python binding.

## Install and run

```powershell
uv sync --dev
uv run xatlas-gui
```

## CLI mode

Supplying `--input` skips the GUI entirely:

```powershell
uv run xatlas-gui --input "C:\Meshes\model.obj" --padding 4 --resolution 2048
```

Choose an output explicitly and suppress normal output (normal output is next to the source file):

```powershell
uv run xatlas-gui `
  --input "C:\Meshes\model.obj" `
  --output "C:\Meshes\model_unwrapped.obj" `
  --padding 8 `
  --resolution 4096 `
  --silent
```

Boolean options support positive and negative forms, for example:

```powershell
uv run xatlas-gui --input model.obj --no-bilinear --block-align --brute-force
```

See every parameter:

```powershell
uv run xatlas-gui --help
```

## Tests and linting

```powershell
uv run pytest
uv run ruff check .
```

## Build the Windows executable

```powershell
powershell -ExecutionPolicy Bypass -File scripts\build.ps1
```

The result is `dist\XAtlasGUI.exe`.

GUI launch:

```powershell
.\dist\XAtlasGUI.exe
```

Silent CLI launch:

```powershell
.\dist\XAtlasGUI.exe --input model.obj --padding 4 --resolution 2048 --silent
```
