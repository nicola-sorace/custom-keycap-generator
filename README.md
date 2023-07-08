# Custom Keycap Generator

> Work in progress. Contributions welcome!
> 
> Intended to fit CherryMX switches, but compatibility is not guaranteed.

Easily generate custom keycap sets for 3d-printing.
This is primarily intended for strange key layouts, such as ergonomic or split keyboards, where pre-made keycap sets are hard to find.

## Dependencies
Requires Python 3.11.
Slightly older versions may work but have not been tested.

Python dependencies:
- [build123d](https://github.com/gumyr/build123d)
- NumPy
- PyYaml
- tqdm

## Usage

Run `python main.py -h` for usage.

```bash
python main.py [style] [layout] -o [output-path] -f [format]
```

Example command to generate a set of keys in `stl` format:

```bash
python main.py default redox
```

Supported formats are inherited from `build123d`:
- stl
- brep
- step
- 3mf

## Configuration

Keycap configuration is done via two `yaml` files: a "style" (located in `configs/styles`), and a "layout" (located in `configs/layouts`).

- The "style" configuration is used to describe a family of keycaps, independent of key layout.
- The "layout" configuration takes a style and defines a specific set of keys with it.

This system is meant to be as flexible as possible.
In a simple case, the style defines the slope angles, roundness, height, etc. of the keys in each row.
It might provide some special modifiers like "convex", "concave", or "flat".
Then, the layout describes the key widths that are required for each row.
It can use the modifiers to asks for special keys, such as a convex space bar.
Additionally, it can ignore the style entirely, and manually override the properties of any keys

> See the `configs` folder for configuration examples.

The styles configuration consists of three lists:
- `global`: These options are automatically inherited by all keys.
- `bases`: Every key can choose one of these as a base configuration.
- `modifiers`: Each key can additionally list any number of modifiers to inherit.

The layout configuration consists of a list of keys.
Each can define (all optional):
- `base`: The chosen base configuration.
- `modifiers`: A list of any number of modifiers to inherit.
- Any additional options.

The default style `configs/styles/default.yaml` describes all available options.

