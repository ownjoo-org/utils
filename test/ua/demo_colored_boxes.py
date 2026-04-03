#!/usr/bin/env python
"""Demonstration of colored boxes with plain text.

This script shows blue bordered boxes with plain uncolored text inside.
The colors will display correctly when run in a terminal that supports ANSI colors.

Usage:
    python test/ua/demo_colored_boxes.py
"""

from ownjoo_toolkit.console.box import Box
from ownjoo_toolkit.console.colors import Color
from ownjoo_toolkit.console.streams import Output

output = Output()


def colored_bordered_box(box, color):
    """Color all box borders (top, bottom, sides) while keeping text plain.

    Args:
        box: Box instance to color
        color: ANSI color code (e.g., Color.BLUE, Color.GREEN)

    Returns:
        String with colored borders and plain text
    """
    lines = str(box).split('\n')
    result = []

    # Characters used for borders (ASCII and Unicode)
    border_chars = set('+-═║╔╗╚╝╭╮╰╯┌┐└┘├┤┬┴┼│─')

    for line in lines:
        if not line:
            result.append(line)
            continue

        # Check if this is a border line (only contains border chars and spaces)
        if all(c in border_chars for c in line.strip()):
            # Top or bottom border - color entire line
            result.append(color + line + Color.RESET)
        elif any(c in '|║' for c in line):
            # Content line with side borders - color the borders, keep text plain
            # Find the positions of the border characters (| or ║)
            side_chars = [i for i, c in enumerate(line) if c in '|║']

            if len(side_chars) >= 2:
                first_pos = side_chars[0]
                last_pos = side_chars[-1]

                left_border = color + line[:first_pos+1] + Color.RESET
                content = line[first_pos+1:last_pos]
                right_border = color + line[last_pos:] + Color.RESET
                result.append(left_border + content + right_border)
            else:
                result.append(line)
        else:
            result.append(line)

    return '\n'.join(result)


def blue_bordered_box(box):
    """Color all box borders blue while keeping text plain."""
    return colored_bordered_box(box, Color.BLUE)


def green_bordered_box(box):
    """Color all box borders green while keeping text plain."""
    return colored_bordered_box(box, Color.GREEN)


def red_bordered_box(box):
    """Color all box borders red while keeping text plain."""
    return colored_bordered_box(box, Color.RED)


def yellow_bordered_box(box):
    """Color all box borders yellow while keeping text plain."""
    return colored_bordered_box(box, Color.YELLOW)


def cyan_bordered_box(box):
    """Color all box borders cyan while keeping text plain."""
    return colored_bordered_box(box, Color.CYAN)


# ============================================================================
# DEMONSTRATIONS
# ============================================================================

print("\n" + "=" * 70)
print("COLORED BOX BORDERS with PLAIN TEXT")
print("=" * 70 + "\n")

# Blue box
print("1. BLUE BORDERS:\n")
box1 = Box(style='double')
box1.add_line('This is plain text')
box1.add_line('The box borders are blue')
box1.add_line('Text remains plain black')
print(blue_bordered_box(box1))

# Green box
print("\n2. GREEN BORDERS:\n")
box2 = Box(style='double')
box2.add_line('This is plain text')
box2.add_line('The box borders are green')
box2.add_line('Text remains plain black')
print(green_bordered_box(box2))

# Red box
print("\n3. RED BORDERS:\n")
box3 = Box(style='double')
box3.add_line('This is plain text')
box3.add_line('The box borders are red')
box3.add_line('Text remains plain black')
print(red_bordered_box(box3))

# Yellow box
print("\n4. YELLOW BORDERS:\n")
box4 = Box(style='double')
box4.add_line('This is plain text')
box4.add_line('The box borders are yellow')
box4.add_line('Text remains plain black')
print(yellow_bordered_box(box4))

# Cyan box
print("\n5. CYAN BORDERS:\n")
box5 = Box(style='double')
box5.add_line('This is plain text')
box5.add_line('The box borders are cyan')
box5.add_line('Text remains plain black')
print(cyan_bordered_box(box5))

# ============================================================================
# MORE EXAMPLES
# ============================================================================

print("\n" + "=" * 70)
print("WITH PADDING")
print("=" * 70 + "\n")

print("Blue box with padding:\n")
box6 = Box(style='ascii', padding=2)
box6.add_line('Extra spacing around text')
box6.add_line('Makes it more readable')
print(blue_bordered_box(box6))

print("\n" + "=" * 70)
print("WITH FIXED WIDTH")
print("=" * 70 + "\n")

print("Green box with fixed width:\n")
box7 = Box(style='ascii', width=60)
box7.add_line('This box has a fixed width')
box7.add_line('All lines fit within 60 characters')
box7.add_line('Extra padding applied automatically')
print(green_bordered_box(box7))

print("\n" + "=" * 70)
print("WITH MULTIPLE LINES")
print("=" * 70 + "\n")

print("Red box with multiple lines:\n")
box8 = Box(style='double')
box8.add_line('First line of content')
box8.add_line('Second line of content')
box8.add_line('Third line of content')
box8.add_line('Fourth line of content')
box8.add_line('Fifth line of content')
print(red_bordered_box(box8))

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70 + "\n")

output.out("You can now:")
output.out("  • Create boxes with colored borders using the functions above")
output.out("  • Keep text plain while coloring borders")
output.out("  • Use any color: BLUE, GREEN, RED, YELLOW, CYAN, MAGENTA, WHITE")
output.out("  • Combine with padding and fixed widths")
output.out("\nAll colors will render correctly in your terminal!")
print()
