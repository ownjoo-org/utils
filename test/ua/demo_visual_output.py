#!/usr/bin/env python
"""Visual demonstration of all output and formatting utilities.

Run this script to see what the formatted output looks like when rendered.
Useful for visual verification and user acceptance testing.

Usage:
    PYTHONIOENCODING=utf-8 python test/ua/demo_visual_output.py
"""

from ownjoo_utils import Box, Color, ColoredText, Output, Table, progress_bar, status_badge, status_line

output = Output()


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


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


# ============================================================================
# BASIC COLORED OUTPUT
# ============================================================================

print_section("1. Basic Colored Output (Output class shorthand methods)")

output.out("Normal text")
output.out_red("Red text")
output.out_green("Green text")
output.out_yellow("Yellow text")
output.out_blue("Blue text")

# ============================================================================
# COMBINED COLORS
# ============================================================================

print_section("2. Combined Colors and Styles")

output.out_colored("Bold Red", color=Color.BOLD + Color.RED)
output.out_colored("Bold Green", color=Color.BOLD + Color.GREEN)
output.out_colored("Dim Yellow", color=Color.DIM + Color.YELLOW)
output.out_colored("Bold Cyan", color=Color.BOLD + Color.CYAN)
output.out_colored("Magenta", color=Color.MAGENTA)
output.out_colored("White on Blue", color=Color.BG_BLUE + Color.WHITE)

# ============================================================================
# COLORED TEXT CHAINING
# ============================================================================

print_section("3. Chainable Colored Text (ColoredText)")

output.out("Simple chain:")
ColoredText().red("Status: ").green("OK").add(" | ").yellow("Duration: ").add("2.5s").out()

output.out("\nComplex multi-segment:")
(
    ColoredText()
    .bold("Build: ")
    .green("OK")
    .add(" | ")
    .bold("Tests: ")
    .green("OK")
    .add(" | ")
    .bold("Deploy: ")
    .red("FAILED")
).out()

output.out("\nUsing Output.segment() builder:")
output.segment().bold("ERROR: ").red("critical failure").out()

# ============================================================================
# STATUS INDICATORS
# ============================================================================

print_section("4. Status Indicators")

output.out("Status lines with color:")
print(status_line("Server", "Running", color=Color.GREEN))
print(status_line("Database", "Offline", color=Color.RED))
print(status_line("Cache", "Warning", color=Color.YELLOW))

output.out("\nStatus badges (semantic coloring):")
print(status_badge("Ready", "ok"))
print(status_badge("Failed", "error"))
print(status_badge("Partial", "warning"))
print(status_badge("Info", "info"))

# ============================================================================
# PROGRESS BARS
# ============================================================================

print_section("5. Progress Bars")

output.out("Progress at different completion levels:")
try:
    print(progress_bar(0, width=30, label="Starting"))
    print(progress_bar(25, width=30, label="Processing"))
    print(progress_bar(50, width=30, label="Halfway"))
    print(progress_bar(75, width=30, label="Almost done"))
    print(progress_bar(100, width=30, label="Complete"))
except UnicodeEncodeError:
    # Fallback for systems that don't support Unicode
    print(progress_bar(0, width=30, label="Starting", filled="=", empty="-"))
    print(progress_bar(25, width=30, label="Processing", filled="=", empty="-"))
    print(progress_bar(50, width=30, label="Halfway", filled="=", empty="-"))
    print(progress_bar(75, width=30, label="Almost done", filled="=", empty="-"))
    print(progress_bar(100, width=30, label="Complete", filled="=", empty="-"))

# ============================================================================
# TABLES
# ============================================================================

print_section("6. Tables with Double-Line Borders and Auto-Detection")

output.out("Table with explicit headers:")
table1 = Table(headers=["Task", "Status", "Duration"], columns=3, style="double")
table1.add_row("Build", "OK", "2.5s")
table1.add_row("Tests", "OK", "5.2s")
table1.add_row("Deploy", "Failed", "-")
print(table1)

output.out("\nTable with dict input (auto-detects headers):")
data = [
    {"name": "Alice", "role": "Admin", "status": "Active"},
    {"name": "Bob", "role": "User", "status": "Active"},
    {"name": "Charlie", "role": "Viewer", "status": "Inactive"},
]
table2 = Table(style="double")
table2.add_rows(data)
print(table2)

output.out("\nTable with key-value pairs:")
settings = [
    ("max_connections", "100"),
    ("timeout", "30s"),
    ("retries", "3"),
]
table3 = Table(style="double")
table3.add_rows(settings)
print(table3)

# ============================================================================
# BOXES
# ============================================================================

print_section("7. Double-Line Boxes with Colors")

output.out("Double-line box:")
box1 = Box(style="double")
box1.add_line("Simple box with double-line borders")
print(colored_bordered_box(box1, Color.CYAN))

output.out("\nBox with padding:")
box2 = Box(style="double", padding=2)
box2.add_line("This box has extra padding for spacing")
print(colored_bordered_box(box2, Color.BLUE))

output.out("\nBox with fixed width:")
box3 = Box(style="double", width=50)
box3.add_line("Fixed width box")
box3.add_line("Multiple lines")
print(colored_bordered_box(box3, Color.GREEN))

# ============================================================================
# INTEGRATED EXAMPLES
# ============================================================================

print_section("8. Integrated: Colored Status Badges in Table")

table_status = Table(headers=["Component", "Status"], columns=2, style="double")
table_status.add_row("API Server", status_badge("OK", "ok"))
table_status.add_row("Database", status_badge("OK", "ok"))
table_status.add_row("Cache", status_badge("SLOW", "warning"))
table_status.add_row("Queue", status_badge("DOWN", "error"))
print(table_status)

print_section("9. Integrated: Colored Borders with Colored Status")

box_status = Box(style="double")
box_status.add_line(status_line("Build", "OK", color=Color.GREEN))
box_status.add_line(status_line("Tests", "OK", color=Color.GREEN))
box_status.add_line(status_line("Lint", "OK", color=Color.GREEN))
box_status.add_line(status_line("Deploy", "Failed", color=Color.RED))
print(colored_bordered_box(box_status, Color.YELLOW))

print_section("10. Integrated: Complex Colored Output")

output.out("Multi-color status report:")
ColoredText().bold("Summary: ").yellow("3 passed").add(", ").red("1 failed").out()
ColoredText().bold("Duration: ").cyan("12.5s").out()
ColoredText().bold("Status: ").red("FAILED").out()

# ============================================================================
# SUMMARY
# ============================================================================

print_section("All Output Utilities Demonstrated Successfully [PASSED]")

output.out("Features demonstrated:")
output.out("  • Basic colored output (red, green, yellow, blue)")
output.out("  • Combined colors and styles (bold, dim, backgrounds)")
output.out("  • Chainable ColoredText for multi-segment coloring")
output.out("  • Status indicators (lines, badges, progress bars)")
output.out("  • Tables with double-line borders and auto-detection")
output.out("  • Boxes with double-line borders, coloring, padding, and fixed width")
output.out("  • Integration of colors with formatters and borders")
print()
