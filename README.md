# Usefull linux console utils

### inidiff

Will compare two INI files and show difference by section.
Position of keys within section doesn't matter.

Usage:
```bash
$ inidiff file1.ini file2.ini
```

### ipshow

Will show `ip addr` output in much more readable format.

Usage:
```bash
$ ipshow
```

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
