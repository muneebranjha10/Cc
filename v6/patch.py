#!/usr/bin/env python3
"""v6 performance/closing experiment. Exact SHA-guarded original Combine CC input."""
import argparse, hashlib, importlib.util, json, pathlib, struct, zipfile, zlib
OLD_SHA="d731fb16db3fee293148731fee962a49432c484dfc5490fea9c8ac94bcd8694c"
root=pathlib.Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location("combinecc_v5",str(root/"v5"/"patch.py"))
v5=importlib.util.module_from_spec(spec)
spec.loader.exec_module(v5)
STEP=0x31a10
BACKDROP=0x4b88c
BODY=0x37780

def replace_hi(b,code,unit,reg,old,new):
 off=code+16+unit*2
 oldbits=struct.unpack("<I",struct.pack("<f",float(old)))[0]>>16
 newbits=struct.unpack("<I",struct.pack("<f",float(new)))[0]>>16
 assert struct.unpack_from("<2H",b,off)==((reg<<8)|0x15,oldbits),f"mismatch at {off:x}"
 struct.pack_into("<H",b,off+2,newbits)

def patch(src):
 b=bytearray(v5.patch(src))
 assert struct.unpack_from("<HHHHII",b,STEP)[:2]==(7,2)
 assert struct.unpack_from("<I",b,STEP+12)[0]==82  # insns_size field at code_off + 12
 assert struct.unpack_from("<HHHHII",b,BACKDROP)[:2]==(6,1)
 assert struct.unpack_from("<I",b,BACKDROP+12)[0]==81
 # 240Hz physics substeps -> 120Hz (reduce per-frame physics work)
 oldbits=struct.unpack("<I",struct.pack("<f",0.004166667))[0]
 newbits=struct.unpack("<I",struct.pack("<f",0.008333334))[0]
 off=STEP+16+0x0c*2
 assert struct.unpack_from("<3H",b,off)==(0x0014,oldbits&0xffff,oldbits>>16)
 struct.pack_into("<I",b,off+2,newbits)
 # 24dp -> 16dp transitioning panel blur
 replace_hi(b,BACKDROP,0x2c,1,24,16)
 # Soften closing/opening tile travel relative to v5
 for unit,reg,old,new in ((0x4f,4,12,8),(0x66,1,10,6),(0x6c,2,8,4),(0x6f,2,22,12)):
  replace_hi(b,BODY,unit,reg,old,new)
 b[12:32]=hashlib.sha1(b[32:]).digest()
 struct.pack_into("<I",b,8,zlib.adler32(b[12:])&0xffffffff)
 return bytes(b)

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--input",required=True);p.add_argument("--output",required=True);p.add_argument("--report")
 a=p.parse_args()
 original=pathlib.Path(a.input)
 sha=hashlib.sha256(original.read_bytes()).hexdigest()
 if sha!=OLD_SHA:raise RuntimeError("Input does not match the inspected CombineCC APK: "+sha)
 output=pathlib.Path(a.output);output.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(original) as base:
  assert base.testzip() is None
  assert base.read("assets/xposed_init")==b"dev.colorcc.Hook\n"
  dex=patch(base.read("classes.dex"))
  with zipfile.ZipFile(output,"w") as result:
   for entry in base.infolist():
    if entry.filename.startswith("META-INF/"):continue
    result.writestr(entry,dex if entry.filename=="classes.dex" else base.read(entry.filename))
 with zipfile.ZipFile(output) as z:
  assert z.testzip() is None and z.read("classes.dex")==dex
 report={"version":"v6 UNTESTED","original_sha256":sha,"changes":["v5 tile anti-shrink and anti-blink","physics integration step 1/240 -> 1/120s","panel blur 24dp -> 16dp","tile travel 22->8dp, header 16->6dp, row 12->4dp, base 36->12dp"],"limitations":"No 120fps guarantee; works with VSYNC Choreographer already; One UI 8/9 hooks not tested"}
 if a.report:pathlib.Path(a.report).write_text(json.dumps(report,indent=2))
 print(json.dumps(report,indent=2))
if __name__=="__main__":main()
