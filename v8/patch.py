#!/usr/bin/env python3
"""Experimental Combine CC v8 whole-panel fade. Exact v7 APK only."""
import argparse,hashlib,json,struct,zipfile,zlib,pathlib
SOURCE_SHA="fdad10b92770925cf9d1a0cf8c7f0b6b0e756ce250d21ceda387afd21583e898"
CODE=0x4f2e8

def patch_dex(blob):
    b=bytearray(blob)
    if b[:4]!=b"dex\n" or struct.unpack_from("<HHHHII",b,CODE)[:2]!=(22,1) or struct.unpack_from("<I",b,CODE+12)[0]!=772:
        raise ValueError("Wrong Panel.update method")
    at=CODE+16+0x240*2
    if struct.unpack_from("<HH",b,at)!=(0x0315,0x4080):
        raise ValueError("Unexpected closing fade instructions")
    struct.pack_into("<H",b,at+2,0x3f80) # 4f -> 1f
    at=CODE+16+0x248*2
    if struct.unpack_from("<H",b,at)[0]!=0xc301:
        raise ValueError("Unexpected opening full-opacity instruction")
    struct.pack_into("<H",b,at,0x5301) # move v3,v5 instead of move v3,v12
    b[12:32]=hashlib.sha1(b[32:]).digest()
    struct.pack_into("<I",b,8,zlib.adler32(b[12:])&0xffffffff)
    return bytes(b)

def patch_manifest(blob):
    b=bytearray(blob)
    old="0.99.v7".encode("utf-16le")
    if b.count(old)!=1:raise ValueError("Not v7 manifest")
    pos=b.find(old);b[pos:pos+len(old)]="0.99.v8".encode("utf-16le")
    def u16(n):return struct.unpack_from("<H",b,n)[0]
    def u32(n):return struct.unpack_from("<I",b,n)[0]
    strings=[];off=8
    while off<len(b):
        typ,hs,size=struct.unpack_from("<HHI",b,off)
        if size<8 or off+size>len(b):raise ValueError("Broken AXML")
        if typ==1:
            count,flags,base=u32(off+8),u32(off+16),u32(off+20)
            if flags&256:raise ValueError("Unexpected UTF-8 string pool")
            for i in range(count):
                p=off+base+u32(off+hs+4*i)
                n=u16(p);p+=2
                if n&0x8000:n=((n&0x7fff)<<16)|u16(p);p+=2
                strings.append(bytes(b[p:p+2*n]).decode("utf-16le"))
        if typ==0x102 and u32(off+20)<len(strings) and strings[u32(off+20)]=="manifest":
            attrs=off+16+u16(off+24);found=0
            for i in range(u16(off+28)):
                p=attrs+i*20;idx=u32(p+4)
                if idx<len(strings) and strings[idx]=="versionCode":
                    if b[p+15]!=0x10 or u32(p+16)!=158:raise ValueError("Wrong versionCode")
                    struct.pack_into("<I",b,p+16,159);found+=1
            if found!=1:raise ValueError("No unique versionCode")
            return bytes(b)
        off+=size
    raise ValueError("No manifest tag")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",required=True)
    ap.add_argument("--output",required=True)
    ap.add_argument("--report")
    args=ap.parse_args()
    src=pathlib.Path(args.input);dst=pathlib.Path(args.output)
    sha=hashlib.sha256(src.read_bytes()).hexdigest()
    if sha!=SOURCE_SHA:raise ValueError("Wrong signed v7 APK SHA256: "+sha)
    dst.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(src) as z:
        if z.testzip():raise ValueError("Broken input ZIP")
        if z.read("assets/xposed_init")!=b"dev.colorcc.Hook\n":raise ValueError("Wrong LSPosed hook")
        dex=patch_dex(z.read("classes.dex"))
        manifest=patch_manifest(z.read("AndroidManifest.xml"))
        with zipfile.ZipFile(dst,"w") as out:
            for entry in z.infolist():
                if entry.filename.startswith("META-INF/"):continue
                data=dex if entry.filename=="classes.dex" else manifest if entry.filename=="AndroidManifest.xml" else z.read(entry)
                out.writestr(entry,data)
    with zipfile.ZipFile(dst) as z:
        if z.testzip() or z.read("classes.dex")!=dex:raise ValueError("Invalid output")
    report={"version":"0.99.v8","versionCode":159,"original":sha,"unsigned_sha256":hashlib.sha256(dst.read_bytes()).hexdigest(),"change":["gesture-following full panel fade on open","linear closing sheet fade","preserve no-stagger tiles and glass shader"],"device_tested":False,"OneUI8_runtime_tested":False,"OneUI9_runtime_tested":False}
    if args.report:pathlib.Path(args.report).write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))

if __name__=="__main__":main()
