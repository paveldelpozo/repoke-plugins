"""Reads and edits index.toml in place, one [[plugin]] block at a time, keeping comments and order."""

import re
import tomllib

PATH = "index.toml"
SEPARATOR = "[[plugin]]\n"


def load():
    with open(PATH, "rb") as f:
        return tomllib.load(f)


def toml_value(value):
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    return '"' + str(value).replace("\\", "\\\\").replace('"', '\\"') + '"'


def set_fields(fields_by_id):
    """`fields_by_id` maps a plugin id to the keys to write; each key replaces its old line."""
    head, *blocks = open(PATH).read().split(SEPARATOR)
    for i, block in enumerate(blocks):
        plugin_id = re.search(r'^id = "(.*)"$', block, re.M).group(1)
        fields = fields_by_id.get(plugin_id)
        if not fields:
            continue
        for key in fields:
            block = re.sub(rf"^{key} = .*\n", "", block, flags=re.M)
        body = block.rstrip("\n")
        gap = block[len(body):]
        lines = "".join(f"\n{key} = {toml_value(value)}" for key, value in fields.items())
        blocks[i] = body + lines + "\n" + gap[1:]
    with open(PATH, "w") as f:
        f.write(SEPARATOR.join([head, *blocks]))
