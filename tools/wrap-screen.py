#!/usr/bin/env python3
"""
Wrap a flat control list into the Source Code schema Studio's newer paste path expects.

The repo stores each screen as a bare top-level control list, which is what Studio's code
view emits when you copy controls. Studio's *screen* paste path -- and the error text
"Make sure to use the Source Code schema, which is the only supported format" -- wants the
document wrapped:

    Screens:
      scrMyActions:
        Properties:
          Fill: =ClrPage
          OnVisible: |-
            =...
        Children:
          - navBg: ...

Wrapping also carries Fill and OnVisible across, so a wrapped paste sets the two screen
properties you would otherwise set by hand.

    python3 tools/wrap-screen.py src/yaml/05-MyActions.pa.yaml scrMyActions \\
        src/screens/scrMyActions.OnVisible.powerfx > src/yaml/wrapped/05-MyActions.pa.yaml

Regenerate the wrapped copy whenever the flat one changes -- nothing checks that they agree.
"""
import sys
from pathlib import Path


def indent(text, spaces):
    pad = " " * spaces
    return "\n".join(pad + line if line.strip() else "" for line in text.split("\n"))


def main():
    if len(sys.argv) not in (3, 4):
        sys.exit(__doc__)

    flat = Path(sys.argv[1]).read_text().rstrip("\n")
    screen = sys.argv[2]

    out = ["Screens:", f"  {screen}:", "    Properties:", "      Fill: =ClrPage"]

    if len(sys.argv) == 4:
        # The OnVisible file is a statement chain; a property value has to be one formula,
        # so it goes in as a block scalar with the leading '=' on its first line. The
        # file's own header comment is dropped so the formula opens on a statement rather
        # than on '=//'; the comments inside the block are literal content and survive.
        lines = Path(sys.argv[3]).read_text().rstrip("\n").split("\n")
        while lines and (not lines[0].strip() or lines[0].lstrip().startswith("//")):
            lines.pop(0)
        out.append("      OnVisible: |-")
        out.append(indent("=" + "\n".join(lines), 8))

    out.append("    Children:")
    out.append(indent(flat, 6))
    print("\n".join(out))


if __name__ == "__main__":
    main()
