#!/usr/bin/env python
# Author : Derivation Bud
#
from __future__ import print_function
import sys,re
if sys.version_info[0] < 3: from io import  BytesIO as IO
else:                       from io import StringIO as IO

def echo(txt) : print(txt,end="") 

sample_in = """
<<x="Context">>
Hello world!
<<echo("This should be displayed.")>>
And this is a loop...
<<
for i in range(3):
   print("  * Looping:{}".format(i))

>>And this is <<echo(x)>> sharing.
"""

sample_out = """

Hello world!
This should be displayed.
And this is a loop...
  * Looping:0
  * Looping:1
  * Looping:2
And this is Context sharing.
"""

def process(data):
    """ Tokenize and ... print or execute..."""

    backup     = sys.stdout 
    sys.stdout = IO() 

    chunks = re.split(r'(<<.*?>>)',data,flags=re.S)
    for chunk in chunks:
        stripped=chunk.split(">>")[0]
        if stripped[:2]=="<<" : 
                                code=compile(stripped[2:],'<string>','exec')
                                exec(code) 
        else                  : print(chunk,end="")

    result = sys.stdout.getvalue()
    sys.stdout.close()
    sys.stdout = backup
    return( result )

def guess(filename):
    """ If input filename contains keywords seed or stem, the output file name
    is simplified.  Else the filename is prefixed"""
    for marker in [".stem","stem.",".seed","seed."]:
        if filename.find(marker)>-1: 
            return (filename.replace(marker,""))

    if "/" in filename:
        index = filename.rfind("/")
        return ( filename[:index+1]+"generated_"+filename[index+1:])
    else:
        return ( "generated_"+filename )

def test():
    assert guess( "path/to/sample.stem.ext")== "path/to/sample.ext"
    assert guess( "path/to/stem.sample.ext")== "path/to/sample.ext"
    assert guess( "path/to/sample.seed.ext")== "path/to/sample.ext"
    assert guess( "path/to/seed.sample.ext")== "path/to/sample.ext"
    assert guess( "sample.ext"             )== "generated_sample.ext"
    assert guess( "path/to/sample.ext"     )== "path/to/generated_sample.ext"
    assert guess( "/path/to/sample.ext"    )== "/path/to/generated_sample.ext"
    assert process( sample_in              )== sample_out
    print("Test PASS")

def cli():
    """ Command line interpreter"""

    import argparse 
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""\
    The intent of this script is to mimic the behavior of a php
preprocessor, but using python syntax. This program parses text 
files and forwards the contents unchanged,  except when marked-up 
segments of python codes are found. In that case the text is executed,
and is substituted with the result of its own execution.""",
        epilog="""
    For example, the input file:
"""+"\n    ".join(sample_in.split("\n"))+"""
    Should result in:"""+"\n    ".join(sample_out.split("\n"))
    )
    parser.add_argument( 'in' ,               help="Input filename")
    parser.add_argument('-v'  , default=False,help='Increase verbosity'
                              , action='store_true')
    parser.add_argument('-out', default=None, help="Output filename, stdout is used if not specified")
    parser.add_argument('-a'  , default=None, help="Output filename is guessed from the input filename"
                              , action='store_true')
    args = vars(parser.parse_args())

    if   args["out"]: dstFile = args["out"]
    elif args[  "a"]: dstFile = guess(args["in"])
    else            : dstFile = None 

    if  args["v"]: print("Processing <- {} ...".format(args["in"]))

    result = process(open(args["in"]).read())

    if dstFile:
        fo=open(dstFile,"w")
        if args["v"]: print("Generating -> {} ...".format(fo.name))
        fo.write( result )
        fo.close()
    else:
        print(result,end="")

if __name__=="__main__":
    if "-t" in sys.argv: test()
    else               : cli()
