#!/usr/bin/env python3
"""
Structural check on the screen YAML in src/yaml/.

This is not a Power Apps validator -- nothing outside Power Apps Studio can tell you
whether a paste will be accepted, because Studio only takes the exact YAML shape its own
code view emits and that shape moves between releases. What this catches is the class of
mistake that is entirely mine to make: malformed YAML, a control declaring the same
property twice, a control with no type, a property value missing its leading '=', a
duplicate control name, or a formula referencing a control that isn't on the same screen.

    python3 tools/validate-screens.py
"""
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML required:  pip install pyyaml")

YAML_DIR = Path(__file__).resolve().parent.parent / "src" / "yaml"


class StrictLoader(yaml.SafeLoader):
    """SafeLoader that rejects duplicate keys instead of letting the last one win.

    Studio does reject them -- PA1001 YamlInvalidSyntax, "Duplicate name 'Color'" -- so a
    control carrying both a default and an override for the same property fails the paste
    outright. PyYAML's default behaviour of silently keeping the last value is exactly
    wrong here: it makes the one file that won't paste look clean.
    """


def _no_duplicate_keys(loader, node, deep=False):
    seen = set()
    for key_node, _ in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in seen:
            raise yaml.constructor.ConstructorError(
                None, None,
                f"duplicate key {key!r}", key_node.start_mark)
        seen.add(key)
    return yaml.SafeLoader.construct_mapping(loader, node, deep=deep)


StrictLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _no_duplicate_keys)

# Properties whose values are designer settings rather than Power Fx formulas.
NON_FORMULA_KEYS = {"Control", "Variant", "Layout", "MetadataKey", "IsLocked", "Group",
                    "ComponentName"}

# Named formulas and user-defined functions declared in App.Formulas.powerfx, plus the
# globals and collections App.OnStart creates. Referencing anything else that looks like
# a bare identifier is worth a second look.
KNOWN_GLOBALS = {
    "ClrPage", "ClrNav", "ClrColumn", "ClrCard", "ClrCardHover", "ClrBorder", "ClrDivider",
    "ClrText", "ClrTextMuted", "ClrTextFaint", "ClrAccent", "ClrAccentHover",
    "ClrAccentText", "ClrDate", "ClrLink", "ClrChip", "ClrChipText", "ClrAvatar",
    "ClrAvatarText", "ClrRiskFill", "ClrRiskText", "ClrOkFill", "ClrOkText",
    "FontUI", "SizePageTitle", "SizeCardTitle", "SizeBody", "SizeMeta", "SizeChip",
    "GapPage", "GapCard", "RadiusCard", "RadiusChip", "BoardColumns",
    "StageAccent", "DueLabel", "Initials", "SafeUrl", "RelativeDay", "Clip",
    "gblUser", "gblMoving", "gblPursuitKey", "gblNewPursuit", "gblPanel", "gblPursuit",
    "gblOverview", "gblExport", "gblExporting", "gblRowMenu", "gblEditKey",
    "gblEditAction", "gblEditDoc", "gblEditUpdate", "gblFields",
    "colActions", "colActions_P", "colPeople", "colPortfolio", "colStages", "colUpdates",
    "colDocs", "colLinks", "colHistory", "colLookups",
    "colFltSI", "colFltHype", "colFltActive", "colFltStage", "colFltStatus",
    "colFltHealth", "colFltEffort", "colFltRisk", "colFltDate",
    "SiteUrl", "PursuitLabel", "PlainText",
    "scrPortfolioBoard", "scrPortfolioList", "scrPursuitWorkspace", "scrPursuitDocsAI",
    "Office365Users", "Parent", "Self", "ThisItem", "Value",
}

# Properties a control type doesn't have. Studio rejects the whole paste with PA2108
# "Unknown property 'X' for control type 'Y'", so a Label converted to another control
# that kept a Label-only property costs you the entire screen.
FORBIDDEN = {
    "HtmlViewer":      {"VerticalAlign", "Wrap", "Align", "FontWeight", "Underline", "Text"},
    "RichTextEditor":  {"VerticalAlign", "Wrap", "Align", "Text", "Mode", "Size", "Color",
                        "Font", "Fill", "BorderColor"},
}

errors, warnings = [], []


def walk(controls, path, names, file):
    """Recurse the control tree, collecting names and checking each property."""
    if not isinstance(controls, list):
        errors.append(f"{file}: {path} should be a list of controls, got {type(controls).__name__}")
        return
    for entry in controls:
        if not isinstance(entry, dict) or len(entry) != 1:
            errors.append(f"{file}: {path} has an entry that isn't a single-key 'Name:' map")
            continue
        name, body = next(iter(entry.items()))
        here = f"{path}/{name}"
        if name in names:
            errors.append(f"{file}: duplicate control name '{name}'")
        names.add(name)

        if not isinstance(body, dict):
            errors.append(f"{file}: {here} has no body")
            continue
        if "Control" not in body:
            errors.append(f"{file}: {here} is missing a Control type")

        ctype = str(body.get("Control", "")).split("@")[0]
        for bad in FORBIDDEN.get(ctype, ()):
            if bad in body.get("Properties", {}):
                errors.append(f"{file}: {here} is a {ctype} and has no '{bad}' property (PA2108)")

        for key, value in body.get("Properties", {}).items():
            if key in NON_FORMULA_KEYS:
                continue
            if not isinstance(value, str):
                errors.append(f"{file}: {here}.{key} is {type(value).__name__}, expected a '=' formula string")
            elif not value.lstrip().startswith("="):
                errors.append(f"{file}: {here}.{key} does not start with '='")

        walk(body.get("Children", []), here, names, file)


def referenced_identifiers(body):
    """Bare Foo.Bar references in formulas, minus quoted strings and column names."""
    found = set()
    for key, value in body.get("Properties", {}).items():
        if key in NON_FORMULA_KEYS or not isinstance(value, str):
            continue
        stripped = re.sub(r'"[^"]*"', '""', value)      # drop string literals
        stripped = re.sub(r"'[^']*'", "''", stripped)   # drop 'Column Name' references
        found.update(re.findall(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\.", stripped))
    return found


def collect_refs(controls, acc):
    for entry in controls or []:
        if not isinstance(entry, dict) or len(entry) != 1:
            continue
        _, body = next(iter(entry.items()))
        if isinstance(body, dict):
            acc.update(referenced_identifiers(body))
            collect_refs(body.get("Children", []), acc)


files = sorted(YAML_DIR.glob("*.pa.yaml"))
if not files:
    sys.exit(f"No .pa.yaml files under {YAML_DIR}")

for path in files:
    try:
        doc = yaml.load(path.read_text(), Loader=StrictLoader)
    except yaml.YAMLError as exc:
        errors.append(f"{path.name}: YAML did not parse -- {exc}")
        continue

    names, refs = set(), set()
    walk(doc, path.stem, names, path.name)
    collect_refs(doc, refs)

    # Power Fx enums (Color.Red, Align.Center, ...) are capitalised the same way controls
    # are, so only flag lower-camel names, which is the convention every control here uses.
    for ref in sorted(refs - names - KNOWN_GLOBALS):
        if ref[0].islower():
            warnings.append(f"{path.name}: '{ref}.…' referenced but no control of that name on this screen")

    print(f"{path.name}: {len(names)} controls")

for w in warnings:
    print(f"  warn  {w}")
for e in errors:
    print(f"  ERROR {e}")

print()
print(f"{len(errors)} errors, {len(warnings)} warnings")
sys.exit(1 if errors else 0)
