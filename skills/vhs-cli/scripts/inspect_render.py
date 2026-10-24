#!/usr/bin/env python3
"""Inspect VHS artifacts via format-aware metadata; optional sampled frame contact sheet."""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


def inspect(path, contact_sheet=None):
    result = {'path': str(path), 'ok': False, 'issues': [], 'metadata': {}}
    if not path.exists(): result['issues'].append('Output missing'); return result
    if path.is_dir():
        frames = sorted(path.glob('*.png'))
        result['metadata'] = {'png_frames': len(frames)}
        if not frames: result['issues'].append('No PNG frames found')
        else: result['ok'] = True
        return result
    size = path.stat().st_size
    result['metadata']['bytes'] = size
    if not size: result['issues'].append('Empty file'); return result
    ext = path.suffix.lower()
    if ext in ('.gif', '.png'):
        try:
            from PIL import Image, ImageOps, ImageDraw
            with Image.open(path) as img:
                result['metadata'].update({'width': img.width, 'height': img.height, 'frames': getattr(img, 'n_frames', 1)})
                if ext == '.gif':
                    times = []
                    for k in range(img.n_frames):
                        img.seek(k)
                        times.append(img.info.get('duration', 0))
                    result['metadata']['duration_seconds'] = round(sum(times)/1000, 3)
                if img.width < 400 or img.height < 180: result['issues'].append('Small frame; check legibility')
                if contact_sheet:
                    indices = sorted(set([0, max(0, img.n_frames//4), max(0, img.n_frames//2), max(0, 3*img.n_frames//4), img.n_frames-1]))
                    thumbs=[]
                    for k in indices:
                        img.seek(k)
                        tile = img.convert('RGB').copy()
                        tile.thumbnail((480, 280))
                        thumbs.append((k,tile))
                    width = max(x.width for _,x in thumbs)
                    sheet=Image.new('RGB',(width,len(thumbs)*310),'white')
                    d=ImageDraw.Draw(sheet)
                    for j,(idx,tile) in enumerate(thumbs):
                        d.text((4,j*310+2),f'frame {idx}',fill='black')
                        sheet.paste(tile,(0,j*310+22))
                    contact_sheet.parent.mkdir(parents=True,exist_ok=True)
                    sheet.save(contact_sheet)
                    result['metadata']['contact_sheet'] = str(contact_sheet)
        except ImportError: result['issues'].append('Pillow unavailable: image metadata inspection skipped')
        except Exception as e: result['issues'].append(f'Image inspection error: {e}')
    elif ext in ('.mp4', '.webm'):
        if shutil.which('ffprobe'):
            proc = subprocess.run(['ffprobe','-v','error','-show_entries','format=duration:stream=width,height,codec_type','-of','json',str(path)],capture_output=True,text=True)
            if proc.returncode: result['issues'].append('ffprobe failed: '+proc.stderr[:300])
            else:
                data=json.loads(proc.stdout)
                result['metadata']['duration_seconds'] = data.get('format',{}).get('duration')
                result['metadata']['streams'] = data.get('streams',[])
                if not any(s.get('codec_type')=='video' for s in data.get('streams',[])):
                    result['issues'].append('No video stream')
        else: result['issues'].append('ffprobe unavailable: video metadata inspection skipped')
    elif ext in ('.ascii','.txt'):
        text=path.read_text(encoding='utf-8',errors='replace')
        result['metadata'].update({'lines':len(text.splitlines()),'characters':len(text)})
    else: result['issues'].append('Unknown extension; only file existence verified')
    result['ok'] = not result['issues']
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('outputs', nargs='+', type=Path)
    p.add_argument('--contact-sheet',type=Path, help='For a single GIF/PNG, save sampled frames to this image')
    p.add_argument('--json',action='store_true')
    args=p.parse_args()
    results=[inspect(f,args.contact_sheet if len(args.outputs)==1 else None) for f in args.outputs]
    if args.json: print(json.dumps(results,indent=2))
    else:
        for r in results: print(f'{"PASS" if r["ok"] else "REVIEW"} {r["path"]}: {r["metadata"]}; {"; ".join(r["issues"])}')
    return 0 if all(r['ok'] for r in results) else 1

if __name__=='__main__': sys.exit(main())
