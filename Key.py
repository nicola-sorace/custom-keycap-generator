from build123d import *
import numpy as np
from dataclasses import dataclass


@dataclass
class KeyConfig:
    tol: float
    tol_tight: float
    wall: float
    inner_rad: float

    key_h: float
    key_r: float

    back_slope: float
    front_slope: float
    side_slope: float
    back_curve: float
    front_curve: float

    front_dy: float
    back_dy: float
    width: float  # As a multiple of `key_h`
    bump: bool = False

class Key:
    def __init__(self, config: KeyConfig):
        self.tol = config.tol
        self.tol_tight = config.tol_tight
        self.wall = config.wall

        self.key_h = config.key_h
        self.key_w = self.key_h * config.width
        self.back_dy = config.back_dy
        self.front_dy = config.front_dy

        self.back_slope = np.radians(config.back_slope)
        self.front_slope = np.radians(config.front_slope)
        self.side_slope = np.radians(config.side_slope)

        self.back_curve = config.back_curve
        self.front_curve = config.front_curve

        self.max_back_height = self.back_dy + max(0.0, -self.back_curve) + 1.0
        self.max_front_height = self.front_dy + max(0.0, -self.front_curve) + 1.0
        self.max_height = max(self.max_back_height, self.max_front_height)

        self.key_r = config.key_r
        self.inner_rad = config.inner_rad
        self.eps = 0.001

        self.cross_height = 4.1 + self.tol
        self.cross_thick = 1.17 + self.tol_tight
        self.stem_depth = 3.8 + self.tol
        self.stem_rad = 0.3

        self.bump = config.bump

    def _outer_key_profile(self, shift: float = 0.0) -> Part:
        """
        Generates the overall (non-hollow) outer shape of the key.
        This is handy for boolean operations. For example, subtracting a
        shifted profile from an un-shifted profile creates a hollow profile.

        :param shift: Distance the profile is shifted by
        """
        key_h = self.key_h + 2*shift
        key_w = self.key_w + 2*shift
        back_dy = self.back_dy + shift
        front_dy = self.front_dy + shift
        key_r = max(0.0, self.key_r + shift)

        """
        Start by constructing a trapezoidal prism.
        This is done via the intersection of two lofts.
        Each loft is between a pair of rectangular faces.
        Optionally, the front and back faces can have a curved top.
        """
        with BuildPart() as part:
            # First loft is between left and right sides (along x-axis)
            with BuildLine() as side_profile:
                Polyline(
                    (-key_h / 2 + np.tan(self.front_slope) * self.max_front_height, self.max_front_height),
                    (-key_h/2, 0),
                    (key_h/2, 0),
                    (key_h / 2 - np.tan(self.back_slope) * self.max_back_height, self.max_back_height),
                    close=True
                )
            with BuildSketch(Plane.YZ.offset(-key_w/2)):
                add(side_profile.line)
                make_face()
            with BuildSketch(Plane.YZ.offset(key_w/2)):
                add(side_profile.line)
                make_face()
            loft()

            # Project front/back heights onto un-sloped planes
            back_dx = np.tan(self.back_slope) * back_dy
            front_dx = np.tan(self.front_slope) * front_dy
            top_slope = (front_dy - back_dy) / (key_h - front_dx - back_dx)
            front_dy_proj = front_dy + top_slope * front_dx
            back_dy_proj = back_dy - top_slope * back_dx

            # Second loft is between front and back faces (along y-axis)
            with BuildSketch(Plane.XZ.offset(-key_h/2)):
                curved = abs(self.back_curve) > self.eps
                back_side_dx = np.tan(self.side_slope) * back_dy_proj
                with BuildLine():
                    Polyline(
                        (-key_w/2 + back_side_dx, back_dy_proj),
                        (-key_w/2, 0),
                        (key_w/2, 0),
                        (key_w/2 - back_side_dx, back_dy_proj),
                        close=not curved
                    )
                    if curved:
                        ThreePointArc(
                            (-key_w/2 + back_side_dx, back_dy_proj),
                            (0, back_dy_proj - self.back_curve),
                            (key_w/2 - back_side_dx, back_dy_proj)
                        )
                make_face()
            with BuildSketch(Plane.XZ.offset(key_h/2)):
                curved = abs(self.front_curve) > self.eps
                front_side_dx = np.tan(self.side_slope) * front_dy_proj
                with BuildLine():
                    Polyline(
                        (-key_w/2 + front_side_dx, front_dy_proj),
                        (-key_w/2, 0),
                        (key_w/2, 0),
                        (key_w/2 - front_side_dx, front_dy_proj),
                        close=not curved
                    )
                    if curved:
                        ThreePointArc(
                            (-key_w/2 + front_side_dx, front_dy_proj),
                            (0, front_dy_proj - self.front_curve),
                            (key_w/2 - front_side_dx, front_dy_proj)
                        )
                make_face()
            loft(mode=Mode.INTERSECT)

            # Finally, round off the edges
            if key_r > 0.0:
                edges = part.edges().group_by(Axis.Z)[1:]
                fillet(
                    sum(edges[1:], edges[0]),
                    key_r
                )
        return part.part

    def _stem(self) -> Part:
        """
        Generates the geometry that fits onto key switch stems
        """
        with BuildPart() as cross:
            # Draw the stem profile and extrude
            with BuildSketch(Plane.XY):
                RectangleRounded(
                    self.cross_height + 2*self.wall,
                    self.cross_height - self.tol,
                    radius=self.wall
                )

                with BuildLine() as line:
                    h = self.cross_height / 2
                    t = self.cross_thick / 2
                    Polyline(
                        (-h, 0), (-h, t), (-t, t), (-t, h), (0, h)
                    )
                    mirror(line.line, about=Plane.XZ)
                    mirror(line.line, about=Plane.YZ)
                make_face(mode=Mode.SUBTRACT)
            stem = extrude(amount=self.stem_depth + self.inner_rad)
            # Alternative to the above line (more flexible, less robust):
            # stem = extrude(until=Until.NEXT)

            # Round edges along extrusion axis
            fillet(stem.edges().filter_by(Axis.Z), self.stem_rad)

            # Extrude a base for the stem if `inner_rad` is defined
            if self.inner_rad > 0.0:
                with BuildSketch(Plane.XY.offset(self.stem_depth + self.inner_rad)):
                    RectangleRounded(
                        self.cross_height + 2*self.wall,
                        self.cross_height - self.tol,
                        radius=self.wall
                    )
                extrude(amount=-self.inner_rad)
        return cross.part

    def shape(self) -> Part:
        """
        Constructs the key's complete shape
        """

        # Construct hollow key shell via boolean operations
        # (avoid `offset` operation since it's completely unreliable)
        outer_profile = self._outer_key_profile()
        shell = outer_profile - self._outer_key_profile(shift=-self.wall)

        # Fill in the top of the key, so that stem is shorter, for strength
        with BuildPart() as top_block:
            with Locations((0.0, 0.0, self.stem_depth + self.inner_rad)):
                Box(
                    2*self.key_w, 2*self.key_h, self.max_height,
                    align=(Align.CENTER, Align.CENTER, Align.MIN)
                )
        filler = outer_profile & top_block.part

        # Add the stem
        cross = self._stem()
        shape = shell + filler + cross

        # Fillet some inside edges, for a bit more strength
        # (this can easily crash if `inner_rad` is too large)
        if self.inner_rad > 0.0:
            shape = shape.fillet(
                self.inner_rad - self.eps,
                shape.faces().filter_by(Axis.Z).group_by(Axis.Z)[2][0].edges()
            )
        
        if self.bump:
            with BuildPart() as bump:
                y = self.stem_depth + self.inner_rad + self.eps
                with BuildSketch(Plane.XY.offset(y)) as sketch:
                    with Locations((0, -0.2 * self.key_h)):
                        Rectangle(6, 2)
                    fillet(sketch.vertices(), 0.999)
                extrude(amount=self.max_front_height - y - 2)
            shape += bump.part

        return shape
