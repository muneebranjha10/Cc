#!/usr/bin/env python3
"""Combine CC v5: guarded DEX bytecode patch for the user's exact input APK."""
import argparse,hashlib,json,struct,zipfile,zlib,pathlib
SHA="d731fb16db3fee293148731fee962a49432c484dfc5490fea9c8ac94bcd8694c"
METHOD=0x37780 # Ldev/colorcc/Panel$Body;->apply()V from exact SHA-guarded input
def patch(src):
 b=bytearray(src)
 assert b[:4]==b"dex\n"
 reg,ins,outs,tries,debug,units=struct.unpack_from("<HHHHII",b,METHOD)
 assert (reg,ins,units)==(11,1,224), "unexpected bytecode layout"
 start=METHOD+16
 def words(unit,expected):
  off=start+unit*2
  got=struct.unpack_from("<"+"H"*len(expected),b,off)
  assert got==tuple(expected), f"wrong DEX instructions at {unit:#x}: {got}"
 def fl(unit,reg,old,new):
  x,y=struct.unpack("<HH",struct.pack("<f",old))
  words(unit,[(reg<<8)|0x14,x,y])
  struct.pack_into("<f",b,start+unit*2+2,new)
 def hi(unit,reg,old,new):
  oldbits=struct.unpack("<I",struct.pack("<f",old))[0]>>16
  newbits=struct.unpack("<I",struct.pack("<f",new))[0]>>16
  words(unit,[(reg<<8)|0x15,oldbits])
  struct.pack_into("<H",b,start+unit*2+2,newbits)
 # Press compression 8% => zero: keep tile/icon scale at 1.0
 fl(0x14,5,0.08,0.)
 # Per-tile closing alpha is driven by close-progress and can flicker.
 # v1 is 1.0 from unit 0x06 through unit 0x44 on this path.
 # Replace mul-float/2addr v0,v1 with move v0,v1; stays constant 1.
 words(0x06,[0x0115,0x3f80])
 words(0x44,[0x10c8])
 struct.pack_into("<H",b,start+0x44*2,0x1001)
 # Carry forward v4's reduced enter movement.
 for unit,reg,old,new in [(0x4f,4,22.,12.),(0x66,1,16.,10.),(0x6c,2,12.,8.),(0x6f,2,36.,22.)]:
  hi(unit,reg,old,new)
 b[12:32]=hashlib.sha1(b[32:]).digest()
 struct.pack_into("<I",b,8,zlib.adler32(b[12:])&0xffffffff)
 return bytes(b)
def main():
 a=argparse.ArgumentParser()
 a.add_argument("--input",required=True)
 a.add_argument("--output",required=True)
 a.add_argument("--report")
 args=a.parse_args()
 f=pathlib.Path(args.input)
 assert hashlib.sha256(f.read_bytes()).hexdigest()==SHA,"wrong source APK"
 out=pathlib.Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(f) as z:
  assert z.testzip() is None
  assert z.read("assets/xposed_init")==b"dev.colorcc.Hook\n"
  dex=patch(z.read("classes.dex"))
  with zipfile.ZipFile(out,"w") as dst:
   for entry in z.infolist():
    if entry.filename.startswith("META-INF/"):continue
    dst.writestr(entry,dex if entry.filename=="classes.dex" else z.read(entry.filename))
 with zipfile.ZipFile(out) as z:assert z.testzip() is None
 report={"source_sha256":SHA,"dex_changes":["tile press scale 0.08 -> 0","tile close alpha -> 1.0","horizontal 22->12dp","header 16->10dp","row 12->8dp","base 36->22dp"],"status":"UNSIGNED; experimental; not One UI 8/9 device tested"}
 if args.report:pathlib.Path(args.report).write_text(json.dumps(report,indent=2))
 print(json.dumps(report,indent=2))
if __name__=="__main__":main()
