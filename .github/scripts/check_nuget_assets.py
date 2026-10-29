"""Check that each declared framework has a resolved NuGet package target."""

import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET


def framework_id(name):
    name = name.lower()
    long_name = re.fullmatch(r'\.(netframework|netstandard|netcoreapp),version=v(\d+(?:\.\d+)+)', name)
    if long_name:
        family, version = long_name.groups()
        return family, tuple(int(part) for part in version.split('.'))
    short_name = re.fullmatch(r'(netstandard|netcoreapp|net)(\d+(?:\.\d+)*)', name)
    if not short_name:
        raise ValueError(f'Unsupported target framework name: {name}')
    family, version = short_name.groups()
    if family == 'net' and '.' not in version:
        family, parts = 'netframework', tuple(int(part) for part in version)
    else:
        parts = tuple(int(part) for part in version.split('.'))
        if family == 'net':
            family = 'netcoreapp' if parts[0] >= 5 else 'netframework'
    return family, parts


def validate(project, assets):
    root = ET.parse(project).getroot()
    declarations = [e.text for e in root.iter() if e.tag in ('TargetFramework', 'TargetFrameworks') and e.text]
    expected = {name.strip() for name in ';'.join(declarations).split(';') if name.strip()}
    if not expected or not expected.issubset(assets['project']['frameworks']):
        raise ValueError(f'Missing target framework inventory: {project}')
    targets = {}
    for name, resolved in assets['targets'].items():
        if '/' in name:  # A runtime-specific target cannot replace the base target.
            continue
        target = framework_id(name)
        if target in targets:
            raise ValueError(f'Duplicate framework target: {project}: {name}')
        targets[target] = resolved
    for name in sorted(expected):
        target = targets.get(framework_id(name), {})
        if not any(item.get('type') == 'package' for item in target.values()):
            raise ValueError(f'Missing or empty resolved package target: {project}: {name}')
    print(f'{project}: verified resolved package targets for {len(expected)} frameworks')


if __name__ == '__main__':
    project = Path(sys.argv[1])
    try:
        validate(project, json.loads((project.parent / 'obj/project.assets.json').read_text()))
    except (KeyError, TypeError, ValueError) as error:
        raise SystemExit(str(error))
