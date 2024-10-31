from build123d import *
from key import KeyConfig, Key
from ocp_vscode import show
import yaml
from stem import stem_from_config

style = 'default'
layout = 'redox'

if __name__ == '__main__':
    with open(f"configs/styles/{style}.yaml") as f:
        style = yaml.safe_load(f.read())
    with open(f"configs/layouts/{layout}.yaml") as f:
        layout = yaml.safe_load(f)
    
    key_name, key_conf = list(layout['keys'].items())[0]
    base = key_conf.pop('base', '')
    modifiers = key_conf.pop('modifiers', [])
    config = (
        style['global'] |
        style['bases'].get(base, {}) |
        key_conf |
        { 'bump': True}
    )
    for mod in modifiers:
        config = config | style['modifiers'][mod]
    stem = stem_from_config(**config.pop('stem', {}))
    key_config = KeyConfig(**config)
    key = Key(key_config, stem)

    show(key.shape())
