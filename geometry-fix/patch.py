#!/usr/bin/env python3
"""Bounded test patch for a single user-supplied Combine CC APK; not a full glass port."""
import argparse, hashlib, json, pathlib, struct, zipfile, zlib

EXPECTED = "d731fb16db3fee293148731fee962a49432c484dfc5490fea9c8ac94bcd8694c"
CODE_OFFSET = 0x37780
PATCHES = (
    (0x14, 5, 0x14, 0.08, 0.02, "press shrink fraction"),
    (0x4f, 4, 0x15, 22., 12., "lateral opening travel dp"),
    (0x66, 1, 0x15, 16., 10., "header opening travel dp"),
    (0x6c, 2, 0x15, 12., 8., "per-row travel dp"),
    (0x6f, 2, 0x15, 36., 22., "base vertical travel dp"),
)

def patch(dex):
    b=bytearray(dex)
    if b[:4] != b"dex\n":
        raise ValueError("Not a DEX")
    registers, ins, outs, tries, debug, size = struct.unpack_from("<4H2I", b, CODE_OFFSET)
    if (registers, ins, size) != (11, 1, 224):
        raise ValueError("Unexpected Body.apply() method layout")
    modifications=[]
    for word, reg, op, old, new, label in PATCHES:
        location=CODE_OFFSET+16+word*2
        actual=struct.unpack_from("<H", b, location)[0]
        if actual != (reg<<8)|op:
            raise ValueError("Unexpected opcode at %#x" % location)
        oldbits=struct.unpack("<I",struct.pack("<f",old))[0]
        newbits=struct.unpack("<I",struct.pack("<f",new))[0]
        if op == 0x15:
            oldval, newval = oldbits>>16, newbits>>16
            at=location+2
            if struct.unpack_from("<H",b,at)[0]!=oldval:
                raise ValueError("Unexpected original number at %#x" % at)
            struct.pack_into("<H",b,at,newval)
        else:
            at=location+2
            if struct.unpack_from("<I",b,at)[0]!=oldbits:
                raise ValueError("Unexpected original number at %#x" % at)
            struct.pack_into("<I",b,at,newbits)
        modifications.append({"name":label,"old":old,"new":new})
    b[12:32]=hashlib.sha1(b[32:]).digest()
    struct.pack_into("<I",b,8,zlib.adler32(b[12:])&0xffffffff)
    return bytes(b),modifications

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",required=True)
    ap.add_argument("--output",required=True)
    ap.add_argument("--report",default="")
    a=ap.parse_args()
    inp=pathlib.Path(a.input)
    actual_sha=hashlib.sha256(inp.read_bytes()).hexdigest()
    if actual_sha!=EXPECTED:
        raise ValueError("Wrong source APK SHA-256: "+actual_sha)
    target=pathlib.Path(a.output)
    target.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(inp) as z:
        if z.testzip(): raise ValueError("Input APK ZIP damaged")
        patched,mods=patch(z.read("classes.dex"))
        if z.read("assets/xposed_init")!=b"dev.colorcc.Hook\n":
            raise ValueError("Unexpected Xposed entry")
        with zipfile.ZipFile(target,"w") as out:
            for meta in z.infolist():
                if meta.filename.startswith("META-INF/"): continue
                out.writestr(meta,patched if meta.filename=="classes.dex" else z.read(meta.filename))
    with zipfile.ZipFile(target) as z:
        if z.testzip(): raise RuntimeError("Damaged output")
        if z.read("classes.dex")!=patched: raise RuntimeError("DEX mismatch")
    report={"source_sha256":actual_sha,"output_sha256":hashlib.sha256(target.read_bytes()).hexdigest(),
            "method":"Ldev/colorcc/Panel$Body;->apply()V","changes":mods,
            "status":"UNSIGNED / NOT DEVICE TESTED / NOT FULL LIQUID GLASS PORT"}
    print(json.dumps(report,indent=2))
    if a.report: pathlib.Path(a.report).write_text(json.dumps(report,indent=2))

if __name__=="__main__": main()
