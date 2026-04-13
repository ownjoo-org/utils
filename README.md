# ownjoo-toolkit

Centralized shared utilities library for all ownjoo-org projects. Provides battle-tested functions for type validation, data parsing, and progress logging.

## Overview

This library is the single source of truth for shared utilities across ownjoo-org projects. All projects should import common utilities from here rather than implementing their own versions.

### Modules

- **`parsing`** — Type validation, datetime conversion, nested data extraction
- **`logging`** — Standardized logging configuration and progress tracking decorators
- **`console`** — Terminal and console output utilities (stdout, stderr, formatting)
- **`data`** — Flexible data handling mixins
- **`asynchronous`** — Async utilities (chunking, generators)

## Installation

Install from PyPI:

```bash
pip install oj-toolkit
```

Or install from the repository:

```bash
pip install git+https://github.com/ownjoo-org/ownjoo-toolkit.git
```

For local development:

```bash
git clone https://github.com/ownjoo-org/ownjoo-toolkit.git
cd ownjoo-toolkit
pip install -e ".[dev]"
```

## Quick Start

### Stream Output

```python
from oj_toolkit import Output

# Create an output handler
output = Output()

# Write to stdout
output.out("Hello", "World")  # Hello World

# Write to stderr
output.err("Error:", "Something went wrong")  # Error: Something went wrong

# Custom separators and line endings
output.out("a", "b", "c", sep="|", end=" - done\n")  # a|b|c - done

# Redirect to custom streams (useful for testing or file output)
import io
file_stream = io.StringIO()
output = Output(stdout=file_stream)
output.out("This goes to the StringIO")
print(file_stream.getvalue())  # This goes to the StringIO\n
```

### Colored Output

```python
from oj_toolkit import Output, Color

output = Output()

# Shorthand methods for common colors
output.out_red("Error message")      # Red text to stdout
output.out_green("Success!")         # Green text to stdout
output.out_yellow("Warning")         # Yellow text to stdout
output.out_blue("Information")       # Blue text to stdout

# Shorthand methods for stderr
output.err_red("Critical error")     # Red text to stderr
output.err_yellow("Minor warning")   # Yellow text to stderr

# Custom color combinations
output.out_colored("Bold Red", color=Color.BOLD + Color.RED)
output.out_colored("Cyan background", color=Color.BG_CYAN)

# Use Color constants directly
from oj_toolkit.console import Color
colored_text = Color.colorize("Important", Color.BOLD + Color.RED)
print(colored_text)
```

### Chainable Colored Text

```python
from oj_toolkit import Output

output = Output()

# Build multi-color lines with a fluent API
output.segment().red("ERROR: ").white("something went wrong").cyan(" (code: 500)").out()

# Chain to stderr
output.segment().bold("Status: ").green("OK").reset(" (2.5s)").err()

# Build a ColoredText independently
from oj_toolkit import ColoredText

text = (ColoredText()
    .bold("Build: ")
    .green("passed")
    .reset(" | ")
    .yellow("warnings: 3")
)
print(text)  # Rendered with ANSI codes
```

### Parsing & Validation

```python
from oj_toolkit import validate, get_datetime, str_to_list, dig

# Validate and convert types
result = validate('123', exp=int, converter=int)  # Returns: 123
result = validate('invalid', exp=int, default=0)  # Returns: 0 (validation failed)

# Convert string to list
items = str_to_list('a,b,c')  # Returns: ['a', 'b', 'c']
items = str_to_list('a;b;c', separator=';')  # Returns: ['a', 'b', 'c']

# Parse datetime from multiple formats
dt = get_datetime('2024-01-15T10:30:00')  # ISO 8601
dt = get_datetime(1705318200)  # Unix timestamp
dt = get_datetime('Mon, 15 Jan 2024 10:30:00 GMT')  # HTTP date

# Extract and validate nested values
data = {'users': [{'name': 'Alice'}, {'name': 'Bob'}]}
name = dig(data, path=['users', 0, 'name'])  # Returns: 'Alice'
name = dig(data, path=['users', 1, 'name'], exp=str)  # Returns: 'Bob'
```

### Logging Setup

Call `configure_logging` once at application startup (Lambda handler, CLI `main()`, FastAPI lifespan). Libraries should never call it — they only use `logging.getLogger(__name__)`.

```python
from oj_toolkit.logging import configure_logging

# Local development — human-readable output, WARNING+
configure_logging(service='my-service')

# Deployed environments — JSON lines to stdout, WARNING+
configure_logging(service='my-service', env='prod')

# Explicit level (int constant or string)
configure_logging(service='my-service', level=logging.INFO)
configure_logging(service='my-service', level='DEBUG')

# Or set LOG_LEVEL env var — configure_logging will read it
# LOG_LEVEL=INFO configure_logging(service='my-service')
```

**Local output** (`env='local'`): human-readable, with level names colorized when stdout is a TTY (`NO_COLOR` and `TERM=dumb` are respected):
```
2026/04/13 12:00:00 - my_module - INFO - started processing
```

**Deployed output** (`env='prod'` or any non-local value):
```json
{"timestamp": "2026-04-13T12:00:00+00:00", "level": "INFO", "logger": "my_module", "service": "my-service", "env": "prod", "message": "started processing"}
```

`configure_logging` is idempotent — safe to call multiple times, only the first call takes effect. Noisy third-party loggers (`urllib3`, `boto3`, `botocore`, `s3transfer`, `requests`) are silenced to WARNING automatically.

**Extending for AWS Lambda** — subclass `JsonFormatter` and override `extra_fields` to inject per-request context:

```python
from oj_toolkit.logging.formatters import JsonFormatter

class LambdaFormatter(JsonFormatter):
    def __init__(self, service, env, context):
        super().__init__(service, env)
        self.context = context

    def extra_fields(self, record):
        return {'aws_request_id': self.context.aws_request_id}
```

### Progress Logging

```python
from oj_toolkit import timed_generator, timed_async_generator
import logging

# configure_logging should be called at app startup before using these decorators
configure_logging(service='my-service', level=logging.INFO)

@timed_generator(log_progress_label="records", log_progress_interval=1000)
def fetch_records():
    for i in range(50000):
        yield {'id': i, 'data': f'record_{i}'}

for record in fetch_records():
    process(record)

# Output:
# 2026/04/13 10:30:00 - oj_toolkit.logging.decorators - INFO - Started records at 2026-04-13T10:30:00+00:00
# 2026/04/13 10:31:00 - oj_toolkit.logging.decorators - INFO - Fetched 1000 records so far
# ... (every 1000 items)
# 2026/04/13 10:35:00 - oj_toolkit.logging.decorators - INFO - Ended records at 2026-04-13T10:35:00+00:00
# 2026/04/13 10:35:00 - oj_toolkit.logging.decorators - INFO - Yielded 50000 records in 0:05:00
```

For async generators:

```python
@timed_async_generator(log_progress_label="items", log_progress_interval=500)
async def fetch_items_async():
    for i in range(10000):
        yield {'id': i}

async for item in fetch_items_async():
    await process(item)
```

## API Reference

### `console` Module

#### `Output(stdout=None, stderr=None)`

Simple wrapper for writing to stdout and stderr streams.

- **Parameters:**
  - `stdout` (TextIO): The output stream for normal output. Default: sys.stdout
  - `stderr` (TextIO): The output stream for error messages. Default: sys.stderr

- **Methods:**

##### `out(*args, sep=' ', end='\n', flush=False)`

Write to standard output stream.

- **Parameters:**
  - `*args`: Values to write (converted to strings)
  - `sep` (str): Separator between args. Default: space
  - `end` (str): String appended after the last value. Default: newline
  - `flush` (bool): Force flush the stream. Default: False

**Example:**

```python
output = Output()
output.out("Hello", "World")  # Hello World
output.out("Status:", "OK", end=" - done\n")  # Status: OK - done
output.out("a", "b", "c", sep="|")  # a|b|c
```

##### `err(*args, sep=' ', end='\n', flush=False)`

Write to standard error stream.

- **Parameters:**
  - `*args`: Values to write (converted to strings)
  - `sep` (str): Separator between args. Default: space
  - `end` (str): String appended after the last value. Default: newline
  - `flush` (bool): Force flush the stream. Default: False

**Example:**

```python
output = Output()
output.err("Error:", "File not found")  # Error: File not found
output.err("code=404", "msg=Not Found", sep="|", flush=True)  # code=404|msg=Not Found
```

**Stream Redirection:**

```python
import io

# Capture output for testing
stdout_capture = io.StringIO()
stderr_capture = io.StringIO()
output = Output(stdout=stdout_capture, stderr=stderr_capture)

output.out("to stdout")
output.err("to stderr")

print(stdout_capture.getvalue())  # to stdout\n
print(stderr_capture.getvalue())  # to stderr\n
```

##### `out_colored(*args, color='', sep=' ', end='\n', flush=False)`

Write colored text to stdout using ANSI escape codes.

- **Parameters:**
  - `*args`: Values to write (converted to strings)
  - `color` (str): ANSI color code (e.g., `Color.RED`, `Color.BOLD + Color.GREEN`)
  - `sep` (str): Separator between args. Default: space
  - `end` (str): String appended after the last value. Default: newline
  - `flush` (bool): Force flush the stream. Default: False

**Example:**

```python
from oj_toolkit import Output, Color

output = Output()
output.out_colored("Error", color=Color.RED)
output.out_colored("Bold Green", color=Color.BOLD + Color.GREEN)
output.out_colored("Status", "OK", color=Color.BLUE)
```

##### `err_colored(*args, color='', sep=' ', end='\n', flush=False)`

Write colored text to stderr using ANSI escape codes. Same parameters as `out_colored()`.

**Example:**

```python
output.err_colored("Critical error", color=Color.BOLD + Color.RED)
```

##### Shorthand Color Methods

Convenient methods for common colors:

- `out_red(*args, ...)` — Red text to stdout
- `out_green(*args, ...)` — Green text to stdout
- `out_yellow(*args, ...)` — Yellow text to stdout
- `out_blue(*args, ...)` — Blue text to stdout
- `err_red(*args, ...)` — Red text to stderr
- `err_green(*args, ...)` — Green text to stderr
- `err_yellow(*args, ...)` — Yellow text to stderr

**Example:**

```python
output = Output()
output.out_green("Success!")
output.out_red("Error occurred")
output.err_yellow("Warning: deprecated")
```

##### `segment() → ColoredText`

Create a chainable `ColoredText` builder bound to this output's streams.

**Example:**

```python
output = Output()
output.segment().red("ERROR: ").white("critical failure").out()
output.segment().yellow("WARNING").cyan(" - deprecated").err()

# Complex multi-color line
(output.segment()
    .bold("Status: ")
    .green("OK")
    .reset(" (")
    .cyan("2.5s")
    .reset(")")
    .out())
```

#### `Color` - ANSI Color Constants and Utilities

Static class providing ANSI color codes for terminal output.

**Attributes:**

- **Reset:** `Color.RESET` — Reset to default terminal color
- **Styles:** `Color.BOLD`, `Color.DIM`
- **Foreground colors:** `Color.RED`, `Color.GREEN`, `Color.YELLOW`, `Color.BLUE`, `Color.MAGENTA`, `Color.CYAN`, `Color.WHITE`
- **Background colors:** `Color.BG_RED`, `Color.BG_GREEN`, `Color.BG_YELLOW`, `Color.BG_BLUE`, `Color.BG_MAGENTA`, `Color.BG_CYAN`, `Color.BG_WHITE`

**Static Methods:**

##### `Color.colorize(text, color='', reset=True)`

Apply ANSI color codes to text.

- **Parameters:**
  - `text` (str): The text to colorize
  - `color` (str): Color code to apply (can be combined with `+`, e.g., `Color.BOLD + Color.RED`)
  - `reset` (bool): Append `Color.RESET` at the end. Default: True

- **Returns:** The text wrapped in color codes

**Example:**

```python
from oj_toolkit import Color

# Single color
colored = Color.colorize("Error", Color.RED)

# Combined colors
important = Color.colorize("CRITICAL", Color.BOLD + Color.RED)

# No reset (continue coloring next output)
colored = Color.colorize("text", Color.GREEN, reset=False)
```

**Available Color Combinations:**

```python
Color.BOLD + Color.RED          # Bold red text
Color.DIM + Color.YELLOW        # Dim yellow text
Color.BOLD + Color.BG_BLUE      # Bold text on blue background
```

#### `ColoredText` - Chainable Colored Text Builder

Accumulates text segments with associated colors and renders them as a single ANSI-coded string.

**Constructor:** `ColoredText(stdout=None, stderr=None)`

**Chaining methods** — each returns `self` for fluent chaining:

- `add(text, color='')` — Add a segment with an explicit color code
- `red(text)`, `green(text)`, `yellow(text)`, `blue(text)` — Shorthand color methods
- `magenta(text)`, `cyan(text)`, `white(text)` — Additional color shorthands
- `bold(text)`, `dim(text)` — Style shorthands
- `reset(text)` — Add text with `Color.RESET` applied
- `from_iter(iterable)` — Consume an iterable of `(text, color)` tuples

**Output methods:**

- `out(sep='', end='\n', flush=False)` — Print to stdout
- `err(sep='', end='\n', flush=False)` — Print to stderr
- `str(text)` — Render as ANSI-coded string
- `iter(text)` — Iterate over `(text, color)` segment tuples

**Example:**

```python
from oj_toolkit import ColoredText, Color

# Fluent chaining
text = (ColoredText()
    .red("ERROR: ")
    .white("something went wrong")
    .cyan(" (code: 500)")
)
print(text)  # Renders with ANSI codes

# Consume a generator of (text, color) tuples
def color_gen():
    yield ("Status: ", Color.BOLD)
    yield ("OK", Color.GREEN)

text = ColoredText().from_iter(color_gen())
text.out()

# Iterate over segments
for segment_text, color in text:
    print(f"{color}{segment_text}\033[0m", end="")
```

### Formatting Utilities

#### `Table` - Smart Table Builder

Build ASCII/Unicode tables with automatic input detection and formatting.

```python
from oj_toolkit import Table, tabulated

# Create a table with dict input (auto-detects headers)
data = [
    {"name": "Alice", "status": "OK"},
    {"name": "Bob", "status": "ERROR"},
]
table = Table()
table.add_rows(data)
print(table)

# Create a table with explicit headers
table = Table(headers=["Name", "Status", "Duration"], columns=3)
table.add_row("Task 1", "OK", "2.5s")
table.add_row("Task 2", "ERROR", "1.2s")
print(table)

# Use as a decorator
@tabulated(headers=["ID", "Value"])
def get_results():
    yield (1, "First")
    yield (2, "Second")
    yield (3, "Third")

get_results()  # Prints results in formatted table

# Customize table appearance
table = Table(headers=["A", "B"], style="rounded", padding=2)
table.add_row("1", "2")
print(table)  # Uses rounded Unicode borders
```

**Styles:** `'auto'` (auto-detect Unicode support), `'ascii'`, `'rounded'`, `'double'`, `'single'`, `'none'`

**Smart Input Detection:**
- Dict input → extracts headers from keys
- List of tuples (2 elements) → treats as key-value pairs
- List of tuples (3+ elements) → treats as rows
- List of strings → treats each as a row

#### `Box` - Text Box Builder

Wrap text in decorative boxes with multiple border styles.

```python
from oj_toolkit import Box, in_box

# Create a simple box
box = Box(style="rounded", padding=1)
box.add_line("Hello from a box")
box.add_line("Multiple lines supported")
print(box)

# Box with title
box = Box(style="double", title="Status", width=30)
box.add_line("Operation complete")
print(box)

# Use as a decorator
@in_box(style="rounded", title="Result")
def show_result():
    return "Success!"

show_result()  # Prints result in a box

# Add multiple lines at once
box = Box(style="ascii")
box.add_lines(["Line 1", "Line 2", "Line 3"])
print(box)
```

**Styles:** `'auto'`, `'ascii'`, `'rounded'`, `'double'`, `'single'`, `'solid'`, `'none'`

#### `status_line` - Format Label-Value Pairs

Format simple status lines with optional colors.

```python
from oj_toolkit import status_line, Color

# Basic status line
output = status_line("Status", "OK")  # Status: OK

# With color
output = status_line("Status", "OK", color=Color.GREEN)

# Custom separator
output = status_line("Name", "Alice", sep=" = ")  # Name = Alice
```

#### `progress_bar` - Text-Based Progress Bar

Display a text-based progress bar with percentage.

```python
from oj_toolkit import progress_bar

# Default bar
bar = progress_bar(75)  # ██████████████░░░░░░   75%

# Custom width and characters
bar = progress_bar(50, width=10, filled="=", empty="-")  # =====-----  50%

# With label
bar = progress_bar(30, width=20, label="Loading")  # Loading: ██████░░░░░░░░░░░░   30%

# All variations
progress_bar(0)      # Empty bar
progress_bar(50)     # Half-filled bar
progress_bar(100)    # Full bar (all filled)
```

#### `status_badge` - Semantic Status Indicators

Display colored status badges with semantic meaning.

```python
from oj_toolkit import status_badge

# Semantic status badges
badge = status_badge("READY", "ok")        # [OK] READY (green)
badge = status_badge("FAILED", "error")    # [ERROR] FAILED (red)
badge = status_badge("PARTIAL", "warning") # [WARNING] PARTIAL (yellow)
badge = status_badge("INFO", "info")       # [INFO] INFO (cyan)
```

**Status types:** `'ok'` (green), `'error'` (red), `'warning'` (yellow), `'info'` (cyan, default)

#### Decorator: `@status_wrapped` - Wrap Function Output with Status

Automatically prepend a status badge to function output.

```python
from oj_toolkit import status_wrapped

@status_wrapped(status="ok")
def operation():
    return "Operation complete"

operation()  # Prints: [OK] Operation complete (in green)

@status_wrapped(status="error")
def failed_operation():
    return "Something went wrong"

failed_operation()  # Prints: [ERROR] Something went wrong (in red)
```

**Example: Combining Formatters**

```python
from oj_toolkit import Table, Box, status_line, Color

# Use formatters together for complex layouts
results = Table(headers=["Task", "Status"])
results.add_row("Build", "OK")
results.add_row("Tests", "OK")
results.add_row("Deploy", "FAILED")

box = Box(style="double", title="Build Summary")
box.add_line(str(results))
print(box)

# Status indicator with color
print(status_line("Overall", "FAILED", color=Color.RED))
```

#### Terminal Detection

##### `detect_color_support() → bool`

Returns `True` if ANSI color output is appropriate for the current environment.

Checks in order: stdout is a real TTY → `NO_COLOR` env var → `TERM=dumb` → `COLORTERM=truecolor|24bit`.

Used internally by `configure_logging` to choose between `ColoredHumanFormatter` and `HumanFormatter`.

```python
from oj_toolkit.console import detect_color_support

if detect_color_support():
    print(Color.GREEN + "ready" + Color.RESET)
else:
    print("ready")
```

##### `detect_unicode_support() → bool`

Returns `True` if the terminal likely supports Unicode characters. Used internally to choose between ASCII and Unicode box/table borders.

### `parsing` Module

#### `validate(v, exp=None, default=None, converter=None, validator=None, **kwargs)`

Generic validation utility that converts and validates a value.

- **Parameters:**
  - `v` (Any): The value to validate
  - `exp` (Type): Expected type. Enables automatic converter selection (list → str_to_list, datetime → get_datetime)
  - `default` (Any): Return this if validation fails. Default: None
  - `converter` (Callable): Custom converter function. Default: auto-selected based on exp
  - `validator` (Callable): Custom validator function(result, exp, **kwargs) → bool. Default: isinstance check
  - `**kwargs`: Passed to converter and validator

- **Returns:** Converted and validated value, or default if validation fails

**Example:**

```python
# Auto-detect converter based on type
numbers = validate('1,2,3', exp=list)  # Returns: ['1', '2', '3']
dt = validate('2024-01-15T10:30:00', exp=datetime)  # Returns: datetime object

# Custom converter and validator
def to_upper(v, *args, **kwargs):
    return str(v).upper()

def is_uppercase(v, *args, **kwargs):
    return v.isupper()

result = validate('hello', converter=to_upper, validator=is_uppercase)
# Returns: 'HELLO'
```

#### `str_to_list(v, separator=',', **kwargs)`

Convert a string to a list by splitting on a separator.

- **Parameters:**
  - `v` (str): The string to split. Non-strings return unchanged
  - `separator` (str): Delimiter to split on. Empty string returns value unchanged
  - `**kwargs`: Additional arguments (unused, for compatibility)

- **Returns:** List of strings, or original value if not a string

**Example:**

```python
str_to_list('a,b,c')  # ['a', 'b', 'c']
str_to_list('a;b;c', separator=';')  # ['a', 'b', 'c']
str_to_list(None)  # None
```

#### `get_datetime(v, format_str=None, **kwargs)`

Parse a value into a datetime object from multiple input formats.

Supports:
- Numeric timestamps (seconds since epoch)
- ISO 8601 strings (YYYY-MM-DDTHH:MM:SS)
- HTTP date format (Sun, 06 Nov 1994 08:49:37 GMT)
- Custom format via `format_str` parameter

- **Parameters:**
  - `v` (datetime | float | str | None): Value to parse
  - `format_str` (str): Custom strptime format string
  - `**kwargs`: Additional arguments (unused)

- **Returns:** datetime object, or None if parsing fails

**Example:**

```python
get_datetime('2024-01-15T10:30:00')  # ISO 8601
get_datetime(1705318200)  # Unix timestamp
get_datetime('Mon, 15 Jan 2024 10:30:00 GMT')  # HTTP date
get_datetime('01/15/2024 10:30:00', format_str='%m/%d/%Y %H:%M:%S')  # Custom
```

#### `dig(src, path=None, post_processor=validate, **kwargs)`

Extract and post-process a value from a nested data structure.

Recursively navigates through nested dicts and lists using a path of keys/indices.

- **Parameters:**
  - `src` (Union[dict, Iterable]): Data structure to navigate
  - `path` (Union[None, int, list, str]): List of keys/indices to navigate. Example: ['data', 0, 'value']
  - `post_processor` (Callable): Function to post-process the found value. Default: validate()
  - `**kwargs`: Passed to post_processor

- **Returns:** Post-processed value, or None if extraction fails

**Example:**

```python
data = {
    'response': {
        'users': [
            {'id': 1, 'name': 'Alice'},
            {'id': 2, 'name': 'Bob'},
        ]
    }
}

# Extract nested value
name = dig(data, path=['response', 'users', 0, 'name'])
# Returns: 'Alice'

# Extract with validation
user = dig(data, path=['response', 'users', 1], exp=dict)
# Returns: {'id': 2, 'name': 'Bob'}

# Extract with custom post-processor
count = dig(data, path=['response', 'users'], post_processor=len)
# Returns: 2
```

### `data` Module

#### `FlexMixin`

Mixin for flexible data handling. Provides dict-like access to instance and class attributes without the rigidity of `@dataclass`.

**Methods:**

- `get(k, default=None)` — Return attribute value by name, or default if not set
- `to_dict()` — Return all non-private attributes (instance + class hierarchy) as a dict

**Example:**

```python
from oj_toolkit.data.flex import FlexMixin

class MyModel(FlexMixin):
    kind: str = 'model'

obj = MyModel(name='Alice', score=42)
obj.get('name')           # 'Alice'
obj.get('missing', 'n/a') # 'n/a'
obj.get('score', 99)      # 42  (falsy-safe — 0, False, '' all work correctly)
obj.to_dict()             # {'kind': 'model', 'name': 'Alice', 'score': 42}
repr(obj)                 # MyModel({'kind': 'model', 'name': 'Alice', 'score': 42})
```

### `logging` Module

#### `configure_logging(service, env='local', level=None)`

Configure the root logger once at application startup.

- **Parameters:**
  - `service` (str): Name of this service/project — appears in every log record
  - `env` (str): Runtime environment. `'local'` → human-readable; anything else → JSON lines. Default: `'local'`
  - `level` (int | str): Log level as `logging.INFO` / `logging.DEBUG` etc., or a name string `'INFO'`/`'DEBUG'`. Falls back to `LOG_LEVEL` env var, then `WARNING`

- **Behavior:**
  - Idempotent — no-op if root logger already has handlers
  - Writes to `sys.stdout`
  - Silences noisy third-party loggers (`urllib3`, `boto3`, `botocore`, `s3transfer`, `requests`) to WARNING

#### `HumanFormatter`

`logging.Formatter` subclass for human-readable local output. Uses `LOG_FORMAT` and `TimeFormats.DATE_AND_TIME`. No color codes — safe for piped/redirected output.

#### `ColoredHumanFormatter`

Subclass of `HumanFormatter` that wraps the level name in ANSI color codes before rendering. The original log record is never mutated (copied per format call).

| Level | Color |
|---|---|
| DEBUG | dim |
| INFO | cyan |
| WARNING | yellow |
| ERROR | red |
| CRITICAL | bold red |

`configure_logging` selects this automatically when `env='local'` and `detect_color_support()` returns True.

#### `JsonFormatter(service, env)`

`logging.Formatter` subclass for structured JSON output. Emits one JSON object per record with fields: `timestamp`, `level`, `logger`, `service`, `env`, `message` (and `exception` if present).

Subclass and override `extra_fields(record) -> dict` to inject additional fields (e.g., `aws_request_id`, `correlation_id`).

#### `timed_generator(log_progress=True, log_progress_label=None, log_progress_interval=10000, log_level=logging.INFO, logger=None)`

Decorator that logs progress and timing for a generator function.

- **Parameters:**
  - `log_progress` (bool): Enable progress logging. Default: True
  - `log_progress_label` (str): Label for progress messages (e.g., "documents"). Default: function name
  - `log_progress_interval` (int): Log progress every N items. Default: 10000
  - `log_level` (int): Logging level (e.g., `logging.INFO`). Default: `logging.INFO`
  - `logger` (logging.Logger): Logger instance. If None, uses root logger — calls `configure_logging` with local defaults if nothing has configured it yet

- **Returns:** Decorated generator

**Example:**

```python
@timed_generator(
    log_progress_label="records",
    log_progress_interval=1000,
    log_level=logging.DEBUG
)
def fetch_records():
    for i in range(50000):
        yield {'id': i}

for record in fetch_records():
    process(record)
```

Logs:
```
Started records at 2024-01-15T10:30:00+00:00
Fetched 1000 records so far
Fetched 2000 records so far
... (every 1000 items)
Ended records at 2024-01-15T10:35:00+00:00
Yielded 50000 records in 0:05:00
```

#### `timed_async_generator(log_progress=True, log_progress_label=None, log_progress_interval=10000, log_level=logging.INFO, logger=None)`

Async version of `timed_generator`. Same parameters and behavior, but for async generators.

**Example:**

```python
@timed_async_generator(
    log_progress_label="items",
    log_progress_interval=500
)
async def fetch_items():
    for i in range(10000):
        yield await api.get_item(i)

async for item in fetch_items():
    await process(item)
```

### `asynchronous` Module

#### `a_chunks(chunk_size, async_iterable)`

Yield successive fixed-size chunks from an async iterable.

- **Parameters:**
  - `chunk_size` (int): Maximum number of items per chunk
  - `async_iterable` (AsyncIterator[T]): The async iterable to chunk

- **Returns:** `AsyncGenerator[List[T], None]` — yields lists of up to `chunk_size` elements. The final chunk may be smaller if the iterable is exhausted.

**Example:**

```python
from oj_toolkit.asynchronous import a_chunks

async def process():
    async def records():
        for i in range(250):
            yield i

    async for batch in a_chunks(100, records()):
        await bulk_insert(batch)  # batches of 100, 100, 50
```

## Development

### Setup

```bash
git clone https://github.com/ownjoo-org/ownjoo-toolkit.git
cd ownjoo-toolkit
pip install -e ".[dev]"
```

### Running Tests

```bash
python -m pytest test/ -v
```

With coverage:

```bash
python -m pytest test/ --cov=oj_toolkit --cov-report=html
```

### Code Style

This project uses `black` for formatting and `ruff` for linting.

```bash
# Format code
black oj_toolkit/

# Check formatting
black --check oj_toolkit/

# Lint
ruff check oj_toolkit/
```

### Testing Guidelines

- Write tests for all new functionality
- Aim for >80% test coverage
- Use pytest for all test files
- See `test/unit/` for examples

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:
- Code standards and conventions
- Testing requirements
- Commit message format
- Pull request process

## Standards

This library follows the ownjoo-org standards defined in [CLAUDE.md](https://github.com/ownjoo-org/claude/blob/main/CLAUDE.md).

Key principles:
- **Simplicity First** — Write the simplest code that solves the problem
- **Pragmatic Testing** — Use integration tests for real dependencies, unit tests for isolation
- **Explicit Commits** — Use conventional commits (feat/fix/refactor/docs/test/chore)
- **Security by Default** — No OWASP Top 10 vulnerabilities, review before commit

## Versioning

This project uses [Semantic Versioning](https://semver.org/):
- **MAJOR** version for incompatible API changes
- **MINOR** version for backward-compatible functionality additions
- **PATCH** version for backward-compatible bug fixes

All changes to the public API should include thorough documentation and example usage.

## License

[See LICENSE file]

## Support

For issues, questions, or contributions, please use the GitHub repository:
- Issues: [github.com/ownjoo-org/ownjoo-toolkit/issues](https://github.com/ownjoo-org/ownjoo-toolkit/issues)
- Pull Requests: [github.com/ownjoo-org/ownjoo-toolkit/pulls](https://github.com/ownjoo-org/ownjoo-toolkit/pulls)
