"""Map Whisper words onto exact Premiere clips and compare independent ASR."""
import argparse,difflib,json,re
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--workdir',required=True,type=Path);p.add_argument('--primary-run',default='qwen-clips');p.add_argument('--comparison-run',default='large-v3-8bit');args=p.parse_args();D=args.workdir.resolve()
mapping=json.loads((D/'clip-map.json').read_text())
clips=mapping['clips'];rows={c['clip']:{'clip':c['clip'],'words':[],'flags':[]} for c in clips}
for f in sorted((D/'raw'/args.comparison_run).glob('group-*.json')):
    data=json.loads(f.read_text())
    for seg in data['segments']:
        for w in seg.get('words',[]):
            a,b=w['edited_start'],w['edited_end'];mid=(a+b)/2
            candidates=[c for c in clips if c['clip'] in data['clip_numbers']]
            c=max(candidates,key=lambda c:(max(0,min(b,c['edited_audio_end'])-max(a,c['edited_audio_start'])),-abs(mid-(c['edited_audio_start']+c['edited_audio_end'])/2)))
            row=rows[c['clip']];row['words'].append(w)
            if w.get('probability',1)<.5: row['flags'].append('low_probability:'+w['word'].strip())
            if b-a<.01: row['flags'].append('zero_duration:'+w['word'].strip())
            if seg.get('avg_logprob',0)<-.8:row['flags'].append('low_segment_probability')
def normalize(t):
    t=re.sub('[أإآ]','ا',t);t=t.replace('ى','ي').replace('ة','ه')
    return re.sub(r'[^\w\s]','',t).lower().split()
for c in clips:
    row=rows[c['clip']]
    row['whisper']=''.join(w['word'] for w in row['words']).strip()
    f=D/f"raw/{args.primary_run}/clip-{c['clip']:03}.json"
    row['qwen']=json.loads(f.read_text())['text'].strip() if f.exists() else None
    row['agreement']=round(difflib.SequenceMatcher(None,normalize(row['whisper']),normalize(row['qwen'] or '')).ratio(),3) if row['qwen'] is not None else None
    if row['agreement'] is not None and row['agreement']<.65:row['flags'].append('model_disagreement')
    if not row['whisper']:row['flags'].append('empty_whisper')
    if row['qwen']=='':row['flags'].append('empty_qwen')
    row['flags']=sorted(set(row['flags']))
(D/'comparison.json').write_text(json.dumps(list(rows.values()),ensure_ascii=False,indent=2))
print('Comparison updated:',len([r for r in rows.values() if r['qwen'] is not None]),'Qwen clips,',len([r for r in rows.values() if r['words']]),'Whisper clips')
for r in rows.values():
    if r['qwen'] is not None:
        print(f"\nCLIP {r['clip']:03} ({r['agreement']}) {', '.join(r['flags'])}\nW: {r['whisper']}\nQ: {r['qwen']}")
