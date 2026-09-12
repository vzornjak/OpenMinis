#!/usr/bin/env python3
"""Validate the Croatian overlay; optionally apply it to a generated string catalog.

Upstream's catalog stays byte-for-byte unchanged. New upstream keys fail the
check rather than silently falling back to English after a merge.
"""
import argparse,json,pathlib,re,sys,collections
ROOT=pathlib.Path(__file__).resolve().parents[2]
PRINTF=re.compile(r'(?<![0-9])%(?:\d+\$)?[-+#0 ]*(?:\d+|\*)?(?:\.(?:\d+|\*))?(?:hh|ll|h|l|L|z|t|j)?[@a-zA-Z%]')
CODE=re.compile(r'`([^`]+)`')
URL=re.compile(r'https?://[^\s)\]`"<>]+')
def load():
 d=json.loads((ROOT/'src/ios/Localizable.xcstrings').read_text())
 tr=json.loads((ROOT/'localization/hr.json').read_text())
 for name in ['hr-overrides.json','apple-hr.json']:
  p=ROOT/'localization'/name
  if p.exists():tr.update(json.loads(p.read_text()))
 return d,tr

def main():
 p=argparse.ArgumentParser();p.add_argument('--apply',type=pathlib.Path);p.add_argument('--allow-incomplete',action='store_true');a=p.parse_args();d,tr=load()
 required={k for k,v in d['strings'].items() if k and v.get('shouldTranslate',True)}
 missing=sorted(required-tr.keys());bad=[]
 for k,v in tr.items():
  if collections.Counter(PRINTF.findall(k))!=collections.Counter(PRINTF.findall(v)):bad.append(k)
  if re.search('[\u0400-\u04ff]',v):bad.append(k)
  if collections.Counter(CODE.findall(k))!=collections.Counter(CODE.findall(v)):bad.append(k)
  if collections.Counter(URL.findall(k))!=collections.Counter(URL.findall(v)):bad.append(k)
 report=ROOT/'.build/localization-gaps.json';report.parent.mkdir(exist_ok=True);report.write_text(json.dumps({'missing':missing,'invalid':sorted(set(bad))},ensure_ascii=False,indent=2)+'\n')
 if missing or bad:
  print(f'Missing: {len(missing)}; invalid placeholders/code/URLs/script: {len(set(bad))}. See {report}')
  if not a.allow_incomplete:return 1
 if a.apply:
  for k,v in tr.items():
   entry=d['strings'].setdefault(k,{})
   entry.setdefault('localizations',{})['hr']={'stringUnit':{'state':'translated','value':v}}
  a.apply.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
 print(f'Croatian: {len(required)-len(missing)}/{len(required)} upstream keys; {len(tr.keys()-required)} additional keys.')
 return 0
if __name__=='__main__':sys.exit(main())
