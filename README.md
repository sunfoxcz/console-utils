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

### mysql_convert_table_engine

Converts tables of specified database to chosen format.

Usage:
```bash
$ mysql_convert_table_engine
Host: localhost
User: user
Password: xxx
Database: test
Target engine (MyISAM, InnoDB): InnoDB
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
