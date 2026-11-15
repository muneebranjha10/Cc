#!/usr/bin/env python3
"""Guarded surgical v7 patch based on the exact published v6 APK. NOT a source reimplementation.

Mitigations: eliminate per-tile movement and hardware-layer promotion,
keep fade stable through most closing gesture, restore stable original spring step.
No promises of on-device correctness or universal One UI support.
"""
from __future__ import annotations
import argparse, hashlib, json, pathlib, struct, zipfile, zlib

SHA_V6 = '0746c5ad0aa2e18f3d79d16d76780f88821535c3cbbf6768475f30a31c465346'
BODY = 0x37780          # Ldev/colorcc/Panel$Body;->apply()V
SPRING = 0x31a10       # Ldev/colorcc/Logic$Spring;->step(F)Z
UPDATE = 0x4f2e8       # Ldev/colorcc/Panel;->update()V


def words(b, pos, expected):
    actual = struct.unpack_from('<'+'H'*len(expected), b, pos)
    if actual != tuple(expected):
        raise ValueError(f'Unexpected instruction at 0x{pos:x}: {actual}, wanted {tuple(expected)}')


def patch_dex(source: bytes):
    b=bytearray(source)
    if b[:8] != b'dex\n035\0' and not b.startswith(b'dex\n'):
        raise ValueError('Input is not a DEX')
    changes=[]
    def validate_method(start, registers, ins, instruction_count):
        hdr=struct.unpack_from('<HHHHII',b,start)
        if hdr[0] != registers or hdr[1] != ins or hdr[5] != instruction_count:
            raise ValueError(f'DEX method changed at 0x{start:x}: {hdr}')
    def high16(code,unit,reg,before,after,comment):
        location=code+16+unit*2
        beforehi=struct.unpack('<I', struct.pack('<f', float(before)))[0]>>16
        afterhi=struct.unpack('<I', struct.pack('<f', float(after)))[0]>>16
        words(b, location, [(reg<<8)|0x15,beforehi])
        struct.pack_into('<H',b,location+2,afterhi)
        changes.append({'patch':comment,'old':before,'new':after})

    validate_method(BODY,11,1,224)
    validate_method(SPRING,7,2,82)
    validate_method(UPDATE,22,1,772)
    # Leave press scale 0% and per-tile alpha 1.0 inherited from v5/v6.
    body_start=BODY+16
    words(b,body_start+0x14*2,[0x0514,0,0])
    words(b,body_start+0x44*2,[0x1001])
    # Existing translation weights after v6: these are effectively applied to
    # each independent icon. Keeping them at zero removes stagger and shrink-looking
    # movement while retaining the panel-level reveal/close and spring physics.
    for unit,reg,old,label in [
        (0x4f,4,8,'horizontal icon travel (dp)'),
        (0x66,1,6,'header travel (dp)'),
        (0x6c,2,4,'per-row vertical stagger (dp)'),
        (0x6f,2,12,'tile vertical travel (dp)'),
    ]:
        high16(BODY,unit,reg,old,0,label)
    # Hardware layer promotions during tile transition allocate GPU textures and
    # can expose flicker. Leave regular hardware-accelerated RenderNode drawing.
    layer_at=body_start+0xd8*2
    words(b,layer_at,[0x2012,0x0228,0x0012,0x0112,0x306e])
    struct.pack_into('<H',b,layer_at,0x0012) # const/4 v0, 0 instead of 2
    changes.append({'patch':'Per-tile forced hardware layer', 'old':'LAYER_TYPE_HARDWARE', 'new':'LAYER_TYPE_NONE'})

    # Restore smaller original integration substep for more stable gestures;
    # v6's 120Hz physics is not a guarantee of 120 rendered frames.
    spring_at=SPRING+16+0x0c*2
    old=struct.unpack('<I',struct.pack('<f',.008333334))[0]
    new=struct.unpack('<I',struct.pack('<f',.004166667))[0]
    words(b,spring_at,[0x0014,old & 0xffff,old>>16])
    struct.pack_into('<I',b,spring_at+2,new)
    changes.append({'patch':'Numerical spring timestep', 'old':'1/120s', 'new':'1/240s (original)'})

    # Retain icon opacity for a larger portion of slow closing while allowing a
    # short final fade instead of abrupt removal. The panel still moves/hides.
    high16(UPDATE,0x240,3,2,4,'Closing sheet fade exponent multiplier')

    b[12:32]=hashlib.sha1(b[32:]).digest()
    struct.pack_into('<I',b,8,zlib.adler32(b[12:]) & 0xffffffff)
    return bytes(b), changes


def patch_manifest(original: bytes) -> bytes:
    # Fixed-size, exact UTF-16LE replacement in AXML string pool: retains offsets.
    before='0.99.58'.encode('utf-16le')
    after='0.99.v7'.encode('utf-16le')
    if len(before)!=len(after) or original.count(before)!=1:
        raise ValueError('Unexpected original binary manifest versionName')
    b=bytearray(original)
    p=b.find(before); b[p:p+len(before)]=after
    # Single typed integer, versionCode attribute in binary XML. Search start
    # tag + attribute entries using AXML chunk structure, not arbitrary bytes.
    def u16(pos):return struct.unpack_from('<H',b,pos)[0]
    def u32(pos):return struct.unpack_from('<I',b,pos)[0]
    strings=[];off=8
    while off<len(b):
        kind,hs,sz=struct.unpack_from('<HHI',b,off)
        if sz<8:raise ValueError('Bad AXML chunk length')
        if kind==1:
            number=u32(off+8);flags=u32(off+16);starts=u32(off+20)
            if flags&256: raise ValueError('Unexpected UTF8 pool')
            for j in range(number):
                q=off+starts+u32(off+hs+j*4)
                n=u16(q);q+=2
                if n & 0x8000:
                    n=(n&0x7fff)<<16|u16(q);q+=2
                strings.append(bytes(b[q:q+2*n]).decode('utf-16le'))
        if kind==0x102:
            nm=u32(off+20)
            if nm<len(strings) and strings[nm]=='manifest':
                astart=off+16+u16(off+24)
                cnt=u16(off+28)
                found=0
                for j in range(cnt):
                    apos=astart+20*j
                    ni=u32(apos+4)
                    if ni<len(strings) and strings[ni]=='versionCode':
                        if b[apos+15]!=0x10 or u32(apos+16)!=157:raise ValueError('Wrong versionCode')
                        struct.pack_into('<I',b,apos+16,158)
                        found+=1
                if found!=1:raise ValueError('versionCode not uniquely found')
                return bytes(b)
        off+=sz
    raise ValueError('Manifest root tag not found')


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--input',required=True)
    ap.add_argument('--output',required=True)
    ap.add_argument('--report')
    a=ap.parse_args()
    src=pathlib.Path(a.input)
    actual=hashlib.sha256(src.read_bytes()).hexdigest()
    if actual!=SHA_V6:raise ValueError('Source not the verified v6 published APK: '+actual)
    dst=pathlib.Path(a.output);dst.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(src) as zin:
        if zin.testzip() is not None:raise ValueError('Source ZIP integrity failed')
        if zin.read('assets/xposed_init')!=b'dev.colorcc.Hook\n':raise ValueError('Missing LSPosed entry point')
        dex,changes=patch_dex(zin.read('classes.dex'))
        manifest=patch_manifest(zin.read('AndroidManifest.xml'))
        with zipfile.ZipFile(dst,'w') as zout:
            for meta in zin.infolist():
                if meta.filename.startswith('META-INF/'):continue
                name=meta.filename
                contents={'classes.dex':dex,'AndroidManifest.xml':manifest}.get(name)
                zout.writestr(meta,contents if contents is not None else zin.read(name))
    with zipfile.ZipFile(dst) as z:
        if z.testzip():raise ValueError('Output ZIP bad')
        if z.read('classes.dex')!=dex or z.read('AndroidManifest.xml')!=manifest:raise ValueError('Changed payload mismatch')
        if z.read('resources.arsc')!=zipfile.ZipFile(src).read('resources.arsc'):raise ValueError('Resources altered')
    report={'version':'v7', 'status':'UNSIGNED; test candidate only',
      'base_sha256':actual,'unsigned_sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),
      'sdk':'min 33, target 36; Android 16 / One UI 8 and Android 17 / One UI 9 NOT runtime tested',
      'glass_renderer':'not modified; real backdrop/FPS compatibility unverified',
      'changes':changes+[{'patch':'Manifest version', 'old':'0.99.58 (157)','new':'0.99.v7 (158)'}]}
    print(json.dumps(report,indent=2))
    if a.report:pathlib.Path(a.report).write_text(json.dumps(report,indent=2))
if __name__=='__main__':main()