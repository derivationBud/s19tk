# s19tk
python2/3 s-records codecs

```
$ ./s19tk.py -h
usage: s19tk.py [-h] [-v] [-in2 IN2] [-out OUT] [-sa SA] [-ea EA] [-sz SZ]
                [-FF] [-00] [-bpl BPL] [-t]
                in1

This utility parses so-called Motorola S-records files. If the optional second
input file is given, these values are merged with the first and have priority
in case of address overlaps. Onces values are imported, they can be exported
to an S19-encoded output file, "as is" or tweaked. Only a subset of addresses
can be output, the number of bytes per line can be specified, and padding can
be added to missing addresses.

positional arguments:
  in1         Mandatory S19-encoded input file, a value of '-' refers to stdin

optional arguments:
  -h, --help  show this help message and exit
  -v          Increase verbosity
  -in2 IN2    Optional S19-encoded input file
  -out OUT    S19-encoded file name, stdout is used if not specified
  -sa SA      Start Address in hex of output data, first address of input(s)
              is used if not specified
  -ea EA      End Address in hex of output data, last address of input(s) is
              used if not specified
  -sz SZ      Size in bytes to be output, 'End Address' is used if not
              specified.
  -FF         Fill gaps with 0xFF
  -00         Fill gaps with 0x00
  -bpl BPL    Maximum bytes per line
  -t          Execute selftest
```
