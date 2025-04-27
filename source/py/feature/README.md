# MapleFont Feature Module

This module provides utilities for defining and managing OpenType font features. It includes tools for creating stylistic sets, character variants, ligatures, and more.

## Overview

The `feature/` module is designed to simplify the creation of OpenType font features. It uses an abstract syntax tree (AST) approach to define and manage features programmatically.

### Key Components

- **`ast.py`**: Core utilities for defining OpenType features.
- **`common.py`**: Shared feature and feature file generation logic.
- **`regular.py`**: Entry file for regular features.
- **`italic.py`**: Entry file for italic features.
- **`base/`**: Foundational classes and features (e.g., numbers, cases, localized forms).
- **`calt/`**: Default ligatures.
- **`cv/`**: Character variants.
- **`ss/`**: Stylistic sets.

## Usage

### Custom Tags

The `calt/tag.py` file provides utilities for creating custom tags.

There are many built-in tags with full-round border in the font, you can use `subst_liga` function to custom trigger text. Following example shows how to convert `TODO:` to `(TODO)` (Cons: the first letter before the tag will be overlapped)

```py
subst_liga(
    source="TODO:",
    target="tag_todo.liga",
    lookup_name="todo_colon"
)
```

If you want to get more tags, use `tag_custom` function:

```py
tag_custom(
    [
      (":attention:", "[attention]"),
      ("_noqa_", "(noqa)"),
      # ("_alter_", "<alter>"),
    ],
    bg_cls_dict,
)
```
This converts:
```
:attention: _noqa_
```

into a styled tag:

![Image](https://github.com/user-attachments/assets/e67f282c-e961-4e55-9169-2f20d7ccfbc6)

#### Limitations

1. Built-in tags are optimized for spacing; custom tags are not.
2. Tags may split if letter spacing > 0. See [#381](https://github.com/subframe7536/maple-font/issues/381#issuecomment-2808022878).
3. Tags inherit the original text color. See [#381](https://github.com/subframe7536/maple-font/issues/381#issuecomment-2809622541).

## Freeze Feature in Variable Format

There are two strategies to freeze a feature:

1. For lookups implementing new ligatures (e.g., `ss08`), move rules into `calt`.
2. For glyph replacements (e.g., `cv01`), substitute glyphs directly with their originals.

Currently, the second approach cannot be implemented in variable format, so in the V7.0 release all variable format variants are identical except for the family name. The build script provides an escape hatch with the `--apply-fea-file` flag.

Since the feature-loading logic was refactored to Python, features are loaded dynamically. The logic in [`common.py`](./common.py) moves rules from the target feature to `calt` (method 1). Enabling the `calt` feature will yield styling equivalent to the static version.

So, please **ENABLE FONT LIGATURE** to make all features work if you are using variable font (NOT recommended).

### AST Utilities

The `ast.py` file provides classes and functions to define OpenType features. Below are some key utilities:

#### `Clazz`

Represents a class of glyphs.

```py
from source.py.feature.ast import Clazz, subst

cls_digit = Clazz("Digit", ["zero", "one", "two", "three"])
cls_digit.state()
subst(cls_digit.use(), "a", "b", "c")
```

Generated fea string:

```fea
@Digit = [zero, one, two, three];
sub @Digit a' b by c;
```

#### `Lookup`

Defines a lookup block for substitutions.

```py
from source.py.feature.ast import Lookup, subst

lookup_example = Lookup(
    name="example_lookup",
    desc="Example substitution",
    content=[
        subst("a", "b", None, "c"),
    ],
)
```

Generated fea string:

```fea
# Example substitution
lookup example_lookup {
  sub a b' by c;
} example_lookup;
```

#### `Feature`

Represents an OpenType feature.

```py
from source.py.feature.ast import Feature

feature_example = Feature(
    tag="calt",
    content=[
        lookup_example,
    ],
)
```

Generated fea string:

```fea
feature calt {

  # Example substitution
  lookup example_lookup {
    sub a b' by c;
  } example_lookup;

}
```

#### Create

Generates the final OpenType feature file content.

```py
from source.py.feature.ast import create

fea_content = create([feature_example])
print(fea_content)
```

### Generating Features

In most of time, you don't need to update the fea files. The generated fea string will be automatically applied at build time without using `--apply-fea-file` flag.

To update existing fea files, you can run:

```sh
uv run task.py fea
```

Here is an example to show how to use the `generate_fea_string` function to generate feature files

```py
from source.py.feature import generate_fea_string

fea_string = generate_fea_string(italic=False, cn=True)
print(fea_string)
```
