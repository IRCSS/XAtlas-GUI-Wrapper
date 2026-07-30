# this is a blender script tested with blender 4.x series. just past this and run it with blenders own python interperter. make sure
# to replace the XATLAS_EXE path with whatever is on your PC 

import bpy
import os
import subprocess
import tempfile
from pathlib import Path


# -------------------------------------------------------------------
# Settings
# -------------------------------------------------------------------

XATLAS_EXE = Path(
    r"D:\Workstation\python\xatlas-gui\dist\XAtlasGUI.exe"
)

PADDING = 4
RESOLUTION = 2048


# -------------------------------------------------------------------
# Validate the active object
# -------------------------------------------------------------------

source_object = bpy.context.active_object

if source_object is None:
    raise RuntimeError("No active object selected.")

if source_object.type != "MESH":
    raise RuntimeError("The active object is not a mesh.")

if not XATLAS_EXE.is_file():
    raise RuntimeError(
        f"XAtlas executable was not found:\n{XATLAS_EXE}"
    )

if bpy.context.mode != "OBJECT":
    bpy.ops.object.mode_set(mode="OBJECT")


# -------------------------------------------------------------------
# Create temporary OBJ paths
# -------------------------------------------------------------------

temp_directory = Path(
    tempfile.mkdtemp(prefix="blender_xatlas_")
)

input_obj = temp_directory / "input.obj"
output_obj = temp_directory / "output.obj"


# -------------------------------------------------------------------
# Select only the active object
# -------------------------------------------------------------------

bpy.ops.object.select_all(action="DESELECT")

source_object.select_set(True)
bpy.context.view_layer.objects.active = source_object


# -------------------------------------------------------------------
# Export the selected object
# -------------------------------------------------------------------

export_result = bpy.ops.wm.obj_export(
    filepath=str(input_obj),
    export_selected_objects=True,
    export_uv=False,
    export_normals=True,
    export_materials=False,
    export_triangulated_mesh=True,
    apply_modifiers=True,
    forward_axis="NEGATIVE_Z",
    up_axis="Y",
)

if "FINISHED" not in export_result:
    raise RuntimeError(f"OBJ export failed: {export_result}")

if not input_obj.is_file():
    raise RuntimeError(
        f"OBJ export did not create the expected file:\n{input_obj}"
    )


# -------------------------------------------------------------------
# Run XAtlas
# -------------------------------------------------------------------

command = [
    str(XATLAS_EXE),
    "--input",
    str(input_obj),
    "--output",
    str(output_obj),
    "--padding",
    str(PADDING),
    "--resolution",
    str(RESOLUTION),
]

startupinfo = None
creationflags = 0

if os.name == "nt":
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = subprocess.SW_HIDE

    creationflags = getattr(
        subprocess,
        "CREATE_NO_WINDOW",
        0,
    )

result = subprocess.run(
    command,
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace",
    startupinfo=startupinfo,
    creationflags=creationflags,
)

if result.returncode != 0:
    raise RuntimeError(
        "XAtlas failed.\n\n"
        f"Exit code: {result.returncode}\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

if not output_obj.is_file():
    raise RuntimeError(
        "XAtlas finished but did not create the output OBJ:\n"
        f"{output_obj}"
    )


# -------------------------------------------------------------------
# Import the unwrapped OBJ
# -------------------------------------------------------------------

objects_before_import = set(bpy.data.objects)

import_result = bpy.ops.wm.obj_import(
    filepath=str(output_obj),
    forward_axis="NEGATIVE_Z",
    up_axis="Y",
)

if "FINISHED" not in import_result:
    raise RuntimeError(f"OBJ import failed: {import_result}")

imported_objects = [
    obj
    for obj in bpy.data.objects
    if obj not in objects_before_import
]

imported_meshes = [
    obj
    for obj in imported_objects
    if obj.type == "MESH"
]

if not imported_meshes:
    raise RuntimeError(
        "The XAtlas OBJ was imported, but no mesh object was created."
    )

unwrapped_object = imported_meshes[0]


# -------------------------------------------------------------------
# Name and select the duplicate
# -------------------------------------------------------------------

unwrapped_object.name = f"{source_object.name}_XAtlas"
unwrapped_object.data.name = f"{source_object.data.name}_XAtlas"

bpy.ops.object.select_all(action="DESELECT")

unwrapped_object.select_set(True)
bpy.context.view_layer.objects.active = unwrapped_object


# -------------------------------------------------------------------
# Verify UVs
# -------------------------------------------------------------------

if not unwrapped_object.data.uv_layers:
    raise RuntimeError(
        "The imported object does not contain a UV layer."
    )

print("XAtlas unwrap completed.")
print(f"Source object: {source_object.name}")
print(f"Imported object: {unwrapped_object.name}")
print(f"UV layers: {len(unwrapped_object.data.uv_layers)}")
print(f"Temporary files: {temp_directory}")