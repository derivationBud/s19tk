#!/usr/bin/env python
"""
Author: Derivation Bud
Date  : Aug17

Implementation of s19-codecs as per description found here:
    https://en.wikipedia.org/wiki/SREC_(file_format)

Usage as a python module:
    Read a byte:
        import s19tk
        data = open("sample.s19").readlines()
        mem  = s19tk.s19decode(data)
        print("byte @ 0x20 : "+mem[0x20])

    Write a byte:
        import s19tk
        data = open("sample.s19").readlines()
        mem  = s19tk.s19decode(data)
        mem[0x20] = 'B7'
        print( "\\n".join(s19tk.s19encode(mem,16)))

"""
from __future__ import print_function, division
import sys
import re

def s19checksum(data):    
    """ Computes the end-of-line checksum from an hex data string"""
    checksum  = sum([int(x,16) for x in re.findall('..',data)])
    return ( checksum & 0xff) ^ 0xff

def s19decode(lines,verbose=False):
    """ 
    Expecting a list 'lines' of S-records. Non-data records are skipped,
    others , such as below, are processed:
     * S1CCAAAADD........DDXX 
     * S2CCAAAAAADD......DDXX
     * S3CCAAAAAAAADD....DDXX
    Where CC = Number of character pairs including: AA,DD,XX
    Where AA = 16 or 24 or 32-bit Address 
    Where XX = CRC over CC,AA,DD
    Returns a dictionary as expected by s19encode."""
    mem = {}
    for line in lines:
        record = line.strip()
        if len(record)>0:
            assert record[0] == 'S'
            assert record[1] in "012356789"
            count  = int(record[2:4], 16)
            assert (len(record)-4)/2==count 

            if   record[1] in '1': dataStart = 8
            elif record[1] in '2': dataStart = 10
            elif record[1] in '3': dataStart = 12
            else:                  dataStart = None # Not a data record

            if dataStart:
                if verbose:
                    crc = int(   record[-2:],16)
                    exp = s19checksum(record[2:-2])
                    if crc != exp:
                        print("Warning! Bad crc ( expecting {:X} ) '{}'".format(exp,record))
                add  = int(record[4:dataStart   ],16)
                data =     record[  dataStart:-2]
                for DD in re.findall("..",data):
                    mem[add]= DD
                    add    += 1
    return( mem )

def s19encode(mem,bpl,verbose=False):
    """ 
    Expecting a dictionary 'mem':
    * Indexed with addresses as integers
    * Containing 2-character hexstrings such as 'A5'
    Returns a list of S3 record lines ready to be printed in a s19 file.
    The 'bpl' parameter specifies the maximum of data bytes per line.
    """
    adds = [k for k in mem.keys()]
    adds.sort(reverse=True)
    lines = []
    line    = ""
    lineAdd = -1
    while adds:
        add   = adds.pop()
        if lineAdd==-1: lineAdd=add
        line += mem[add]
        # If end-of-file or jump in addresses or end-of-line
        if len(adds)==0  or (adds[-1]!= add+1) or len(line)==bpl*2:
            line = "{:08X}".format(lineAdd)    +line
            line = "{:02X}".format(len(line)//2+1)+line
            line = line+"{:02X}".format(s19checksum(line))
            line = "S3"+line
            lines.append(line)
            line    = ""
            lineAdd = -1
    return(lines)

def test():
    """ Unit testing """
    assert s19checksum("0000000000000000"   )==0xFF
    assert s19checksum("0102040810204080"   )==0x00
    assert s19checksum(      "04123456"     )==0x5F
    assert s19checksum(      "0512345678"   )==0xE6
    assert s19checksum(      "06123456789A" )==0x4B

    assert s19decode(     ["S1041234565F"    ],True)=={0x1234:'56'}
    assert s19decode(     ["S20512345678E6"  ],True)=={0x123456:'78'}
    assert s19decode(     ["S306123456789A4B"],True)=={0x12345678:'9A'}

    assert s19encode({0x12345678:'9A'},20)==["S306123456789A4B"]
    assert s19encode({0:'A0',1:'A1',2:'A2',3:'A3'},20)==['S30900000000A0A1A2A370']
    assert s19encode({0:'A0',1:'A1',2:'A2',3:'A3'}, 4)==['S30900000000A0A1A2A370']
    assert s19encode({0:'A0',1:'A1',2:'A2',3:'A3'}, 2)==['S30700000000A0A1B7', 
                                                         'S30700000002A2A3B1']
    assert s19encode({0:'A0',1:'A1',2:'A2',3:'A3'}, 1)==['S30600000000A059', 
                                                         'S30600000001A157', 
                                                         'S30600000002A255',
                                                         'S30600000003A353']
    print("Test PASS")

def cli():
    """Command Line interpreter, and main sequencer:
    1. inputs data from in1
    2. optionally imports data from in2
    3. optionally keeps only the requested address range
    4. optionally fills the gaps in
    5. dumps the result either to stdout or to the specified file
    """

    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.description="""This utility parses so-called Motorola S-records files. If the
        optional second input file is given, these values are merged with the first
        and have priority in case of address overlaps. Onces values are imported, they 
        can be exported to an S19-encoded output file, "as is" or tweaked. Only a 
        subset of addresses can be output, the number of bytes per line can be 
        specified, and padding can be added to missing addresses.
        """
    parser.add_argument( 'in1',                help="Mandatory S19-encoded input file, a value of '-' refers to stdin")
    parser.add_argument('-v',   default=False, help='Increase verbosity', action='store_true')
    parser.add_argument('-in2', default=None,  help="Optional S19-encoded input file")
    parser.add_argument('-out', default=None,  help="S19-encoded file name, stdout is used if not specified")
    parser.add_argument('-sa' , default=None,  help="Start Address in hex of output data, first address of input(s) is used if not specified")
    parser.add_argument('-ea' , default=None,  help="End Address in hex of output data, last address of input(s) is used if not specified")
    parser.add_argument('-sz' , default=None,  help="Size in bytes to be output, 'End Address' is used if not specified.",type=int)
    parser.add_argument('-FF' , default=False, help="Fill gaps with 0xFF", action='store_true')
    parser.add_argument('-00' , default=False, help="Fill gaps with 0x00", action='store_true')
    parser.add_argument('-bpl', default=16,    help="Maximum bytes per line",type=int)
    parser.add_argument('-t',   default=False, help="Execute selftest", action='store_true')
    args = vars(parser.parse_args())

    if args["v"] : 
        print("Using these settings:")
        for k,v in args.items(): 
            print("> {:6} : {}".format(k,v))

    if args["t"] : test()

    #-------------- Importing data from input files

    mem = {}
    if True:
        if args["v"] : 
            print("Reading: {} ...".format(args["in1"]))
        if args["in1"]=="-":
            data = sys.stdin.readlines()
        else:            
            data = open(args["in1"]).readlines()
        mem.update(s19decode(data,args["v"]))

    if args["in2"] :
        if args["v"] : 
            print("Reading: {} ...".format(args["in2"]))
        data = open(args["in2"]).readlines()
        mem.update(s19decode(data,args["v"]))
    
    #-------------- Selecting address range

    if args["sa"]:   startAt = int(args["sa"],16)
    else:            startAt = min(mem.keys())

    if   args["sz"]: stopAt = startAt+int(args["sz"])-1
    elif args["ea"]: stopAt = int(args["ea"],16)
    else:            stopAt = max(mem.keys())

    for add in list(mem.keys()):
        if not startAt<=add<=stopAt:
            mem.pop(add)

    #-------------- Filling

    if args["00"] or args["FF"]:
        for add in range(startAt,stopAt+1):
            if add not in mem:
                if args["00"]: mem[add]='00'
                if args["FF"]: mem[add]='FF'

    #-------------- Dumping

    if args["out"]: 
        out=open(args["out"],"w")
        if args["v"]:
            print("Creating: {}".format(out.name))
    else:           
        out=sys.stdout

    for line in s19encode(mem,args["bpl"],args["v"]):
        out.write("{}\n".format(line))

if __name__=="__main__": 
    if "-t" in sys.argv: test() 
    else               : cli()

