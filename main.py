from build123d import *
import argparse
import os
import yaml
from tqdm import tqdm
from Key import KeyConfig, Key

parser = argparse.ArgumentParser(
    "Custom Keycap Generator",
    "Generate custom print-ready keycap geometries",
    "Work in progress. Contributions welcome."
)
parser.add_argument('style')
parser.add_argument('layout')
parser.add_argument('-o', '--output-path', default="output")
parser.add_argument('-f', '--format', default='stl', choices=['stl', 'brep', 'step', '3mf'])

if __name__ == '__main__':
    args = parser.parse_args()

    with open(f"configs/styles/{args.style}.yaml") as f:
        style = yaml.safe_load(f.read())
    with open(f"configs/layouts/{args.layout}.yaml") as f:
        layout = yaml.safe_load(f)

    print(f"Generating {len(layout['keys'])} keys...")
    for key_name, key_conf in tqdm(layout['keys'].items()):
        base = key_conf.pop('base', '')
        modifiers = key_conf.pop('modifiers', [])
        config = (
                style['global'] |
                style['bases'].get(base, {}) |
                key_conf
        )
        for mod in modifiers:
            config = config | style['modifiers'][mod]
        config = KeyConfig(**config)
        key = Key(config)

        out_path = os.path.join(args.output_path, f"{key_name}.{args.format}")
        if args.format == 'stl':
            key.shape().export_stl(out_path)
        elif args.format == 'brep':
            key.shape().export_brep(out_path)
        elif args.format == 'step':
            key.shape().export_step(out_path)
        elif args.format == '3mf':
            key.shape().export_3mf(out_path, 1e-3, 0.1, Unit.MILLIMETER)
