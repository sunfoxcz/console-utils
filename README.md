# Usefull linux console utils

### inidiff

Will compare two INI files and show difference by section.
Position of keys within section doesn't matter.
Requires Python 3.12 or newer. Keys are case-sensitive; values are compared
literally, without interpolation. Keys before the first section are supported.

Usage:
```bash
$ inidiff file1.ini file2.ini
```

### xmldiff

Compares child fields of XML elements selected by an XPath expression.
Requires Python 3.12 or newer and `lxml` (`python3 -m pip install lxml`).

Usage:
```bash
$ xmldiff file1.xml file2.xml '//item' -c id -i updated_at,checked_at
```

`-c` / `--compare-tag` matches records by the value of a child tag; without it,
records are matched by position. Comparison keys must be non-empty and unique.
`-i` / `--ignore-tags` excludes comma-separated child tag names from comparison.
Both options use exact tag names (Clark notation, `{namespace}tag`, for namespaced
tags). XPath expressions can use `local-name()` to select namespaced elements.
Child fields are indexed by tag name; if a tag repeats, the last value is used.
Nested XML is compared as text after removing indentation whitespace; nested
element order remains significant. Record attributes and direct record text are
outside the comparison.

### Diff output and colors

Both diff tools show removed values with `-`, added values with `+`, and changed
values with `<` (old) and `>` (new). Old values are red and new values are green
when stdout is a terminal. Color control, in priority order:

1. `--no-color` always disables ANSI colors.
2. A non-empty [`NO_COLOR`](https://no-color.org/) disables colors.
3. A non-empty [`FORCE_COLOR`](https://force-color.org/) enables colors, including
   when stdout is redirected.
4. Otherwise, colors follow stdout's terminal detection.

Empty environment values are ignored; any non-empty value (including `0`) counts
as set. `NO_COLOR` wins when both variables are set.

Both tools accept `-h`, `-?`, and `--help`. A completed comparison exits with `0`,
including when differences are found; file or content errors exit with `1`, and
invalid command-line arguments with `2`. Errors are written to stderr.

Run the regression tests with Python 3.12+ and `lxml` installed:
```bash
$ python3 -m unittest discover -s tests -v
```

### ipshow

Shows network interfaces, link types, MAC addresses, and IPv4/IPv6 addresses
with prefix lengths in a compact format. Requires Python 3.12 or newer and
`ip` from iproute2 with JSON support (`ip -json address show`). No Python
packages are required.

Interface names containing dots, hyphens, or other characters are supported.
Names occupy a column sized to the longest name; types and IP addresses align
in the next column. Type and MAC fields are separated by a single space.
Missing MAC addresses are shown as `-`; interfaces without IP addresses are
also listed. Errors are written to stderr and exit with status `1`; invalid
command-line arguments exit with `2`.

Usage:
```bash
$ ipshow
```

Use `-h`, `-?`, or `--help` for help.

### mysql_convert_table_collation

Converts database, tables and columns of specified collation to target collation.

Usage:
```bash
$ mysql_convert_table_collation [OPTIONS] <database> <from_collation> <to_collation>
$ mysql_convert_table_collation [OPTIONS] test utf8_general_ci utf8mb4_unicode_ci
```

Help:
```bash
$ mysql_convert_table_collation --help
```

### mysql_convert_table_engine

Converts tables of specified database to chosen format.

Usage:
```bash
$ mysql_convert_table_engine [OPTIONS] <database> <myisam|innodb>
```

Help:
```bash
$ mysql_convert_table_engine --help
```

### mysql_compare_cross_table_columns

Compares tables in specified database by engine, collation, field definitions
of same field names and shows differences.

Usage:
```bash
$ mysql_compare_cross_table_columns [OPTIONS] <database>
```

Help:
```bash
$ mysql_compare_cross_table_columns --help
```

### postqueue_filter

Filter Postfix mail queue by recipient, sender or invalid dns lookup and possibly delete it.

Help:
```bash
$ postqueue_filter -h
```

Show messages by recipient:
```bash
$ postqueue_filter -r some@recipient.com
```

Delete messages by sender:
```bash
$ postqueue_filter -s some@sender.com -d
```

Show and delete messages undeliverable because of invalid MX record:
```bash
$ postqueue_filter -i
$ postqueue_filter -i -d
```

### pwgen

Generates random password using characters, which doesn't look similar.

Usage:
```bash
$ pwgen
PWD: ChHEMkbUANAQSZND
$ pwgen 24
PWD:  QGKST5Wp7g4TVFzk3y7hh5D5
```
