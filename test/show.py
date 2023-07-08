"""
Useful debug script to visualize build123d objects
Monkey-patches a `BuildPart.show()` function
Requires the pyvista library
"""

from build123d import *
import pyvista

tmp_stl = "test.stl"
tmp_brep = "test.stl"


def show_build_part(self: BuildPart):
    self.part.export_stl(tmp_stl)
    self.part.export_brep(tmp_brep)
    pyvista.get_reader(tmp_stl).read().plot(background="#282C34")
BuildPart.show = show_build_part


def show_part(self: Part):
    self.export_stl(tmp_stl)
    self.export_brep(tmp_brep)
    pyvista.get_reader(tmp_stl).read().plot(background="#282C34")
Part.show = show_part
