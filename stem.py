from build123d import *
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable

def stem_from_config(**config):
    stem_type = config.pop('type', 'minimal')
    return {
        'formal': StemFormal,
        'reinforced': StemReinforced,
        'minimal': StemMinimal,
    }[stem_type](**config)

@dataclass
class Stem(ABC):
    # Official Cherry MX keycap stem dimensions
    cross_height: float = 4.1
    cross_thick: float = 1.17
    stem_depth: float = 3.8
    stem_rad: float = 5.5 / 2
    stem_inner_rad: float = 0.3

    @abstractmethod
    def build(self, key: 'Key') -> Part:
        """
        Generates the geometry that fits onto key switch stems
        """

    def select_inner_rad_edges(self, key: 'Key', part: BuildPart) -> Iterable[Edge]:
        """
        Select the edges that should be filleted with inner_rad
        """
        return part.faces().filter_by(Axis.Z).group_by(Axis.Z)[2][0].edges()

@dataclass
class StemFormal(Stem):
    tol: float = 0.05

    def _cross(self) -> Sketch:
        with BuildSketch(Plane.XY) as cross:
            Rectangle(self.cross_thick + self.tol, self.cross_height + self.tol)
            Rectangle(self.cross_height + self.tol, self.cross_thick + self.tol)
            fillet(
                cross.vertices().sort_by_distance(Vector(0, 0, 0))[:4],
                self.stem_inner_rad,
            )
        return cross.sketch

    def build(self, key: 'Key') -> Part:
        with BuildPart() as stem:
            with BuildSketch(Plane.XY):
                Circle(self.stem_rad)
            extrude(amount=key.stem_depth + key.inner_rad + 0.001)
            extrude(self._cross(), amount=self.stem_depth, mode=Mode.SUBTRACT)
        return stem.part

    def select_inner_rad_edges(self, key: 'Key', part: BuildPart) -> Iterable[Edge]:
        """
        Select the edges that should be filleted with inner_rad
        """
        return part.faces().filter_by(Axis.Z).group_by(Axis.Z)[2].edges()

@dataclass
class StemReinforced(StemFormal):
    reinforce_w = 6.0
    reinforce_h = 4.0
    reinforce_rad = 0.4

    def build(self, key: 'Key') -> Part:
        with BuildPart() as stem:
            with BuildSketch(Plane.XY):
                Circle(self.stem_rad)
                RectangleRounded(
                    self.reinforce_w,
                    self.reinforce_h,
                    self.reinforce_rad,
                )
            extrude(amount=key.stem_depth + key.inner_rad + 0.001)
            extrude(self._cross(), amount=self.stem_depth, mode=Mode.SUBTRACT)
        return stem.part

@dataclass
class StemMinimal(Stem):
    tol: float = 0.05

    def build(self, key: 'Key') -> Part:
        with BuildPart() as cross:
            # Draw the stem profile and extrude
            with BuildSketch(Plane.XY):
                RectangleRounded(
                    self.cross_height + self.tol + 2*key.wall,
                    self.cross_height,
                    radius=key.wall
                )

                with BuildLine() as line:
                    h = (self.cross_height + self.tol) / 2
                    t = (self.cross_thick + self.tol) / 2
                    Polyline(
                        (-h, 0), (-h, t), (-t, t), (-t, h), (0, h)
                    )
                    mirror(line.line, about=Plane.XZ)
                    mirror(line.line, about=Plane.YZ)
                make_face(mode=Mode.SUBTRACT)
            stem = extrude(amount=self.stem_depth + key.inner_rad + 0.1)
            # Alternative to the above line (more flexible, less robust):
            # stem = extrude(until=Until.NEXT)

            # Round edges along extrusion axis
            fillet(stem.edges().filter_by(Axis.Z), key.stem_rad)

            # Extrude a base for the stem if `inner_rad` is defined
            if key.inner_rad > 0.0:
                with BuildSketch(Plane.XY.offset(self.stem_depth + key.inner_rad + 0.1)):
                    RectangleRounded(
                        self.cross_height + self.tol + 2*key.wall,
                        self.cross_height,
                        radius=key.wall
                    )
                extrude(amount=-key.inner_rad)
        return cross.part
