#!/usr/bin/env python3
"""Modify ColorCC's existing AGSL lens renderer without changing Xposed hooks."""
import argparse
import hashlib
import pathlib
import re
import struct
import zlib
import zipfile

PREFIX = b'uniform shader backdrop;\nuniform shader soft;\n'

def uleb(data, pos):
    value = 0
    shift = 0
    while True:
        part = data[pos]
        pos += 1
        value |= (part & 0x7f) << shift
        if not part & 0x80:
            return value, pos
        shift += 7

def minify(shader):
    shader = re.sub(r'\s+', ' ', shader)
    return re.sub(r'\s*([{}();,+*/=<>])\s*', r'\1', shader)

def lens_shader(original):
    # Preserve the same uniform interface as ColorCC 0.99.58.
    shader = original.replace(
        'float2 at = base * scale;\n    env = backdrop.eval(at).rgb;',
        '''float lensW = clamp(min(h.x, h.y) * 0.32, 6.0, 36.0);
    float x = clamp(1.0 + d / lensW, 0.0, 1.0);
    float bend = (1.0 - sqrt(max(1.0 - x * x, 0.0))) * lensW * 0.62;
    float2 at = (base - n * bend) * scale;
    float2 dispersion = n * bend * (0.065 * scale);
    env = half3(backdrop.eval(at + dispersion).r,
                backdrop.eval(at).g,
                backdrop.eval(at - dispersion).b);''')
    shader = shader.replace(
        'float2 bt = base * beforeScale;',
        'float2 bt = (base - n * bend) * beforeScale;')
    shader = shader.replace(
        'c = mix(env, half3(1.0), 0.55) * line + c * (1.0 - line);',
        '''half glint = half(0.12 * pow(clamp(1.0 + d / max(6.0, min(h.x, h.y) * 0.32), 0.0, 1.0), 2.0) * pow(max(lit, 0.0), 2.0));
  c = mix(env, half3(1.0), 0.55) * line + c * (1.0 - line);
  c = min(c + half3(glint * a), half3(a));''')
    if shader == original:
        raise ValueError('Expected source code patterns were not found')
    return minify(shader)

def patch_dex(data):
    result = bytearray(data)
    string_count, strings_offset = struct.unpack_from('<II', result, 0x38)
    matches = []
    for index in range(string_count):
        off = struct.unpack_from('<I', result, strings_offset + 4 * index)[0]
        utf16_len, start = uleb(result, off)
        if result[start:start + len(PREFIX)] != PREFIX:
            continue
        end = result.index(0, start)
        original = result[start:end].decode('utf-8')
        if len(original) != utf16_len:
            raise ValueError('Unexpected UTF-8 / UTF-16 string data')
        enhanced = lens_shader(original)
        if len(enhanced) > len(original):
            raise ValueError('Lens shader exceeds original DEX string slot')
        replacement = (enhanced + ' ' * (len(original) - len(enhanced))).encode('ascii')
        result[start:end] = replacement
        matches.append((len(original), len(enhanced)))
    if len(matches) != 1:
        raise ValueError(f'Expected exactly 1 ColorCC lens shader: found {len(matches)}')
    result[12:32] = hashlib.sha1(result[32:]).digest()
    struct.pack_into('<I', result, 8, zlib.adler32(result[12:]) & 0xffffffff)
    return bytes(result), matches[0]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    src, dst = pathlib.Path(args.input), pathlib.Path(args.output)
    dst.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(src) as original:
        dex, detail = patch_dex(original.read('classes.dex'))
        with zipfile.ZipFile(dst, 'w') as output:
            for member in original.infolist():
                if member.filename.startswith('META-INF/'):
                    continue
                output.writestr(member, dex if member.filename == 'classes.dex' else original.read(member.filename))
    print('Updated ColorCC lens shader:', detail, 'unsigned APK:', dst)

if __name__ == '__main__':
    main()
