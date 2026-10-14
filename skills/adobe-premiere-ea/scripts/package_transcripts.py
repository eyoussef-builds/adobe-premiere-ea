"""Package reviewed per-clip text with exact manifest timecodes and an index."""
import argparse,csv,hashlib,json,zipfile
from fractions import Fraction
from pathlib import Path

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--workdir',required=True,type=Path);p.add_argument('--reviewed',required=True,type=Path);a=p.parse_args()
 D=a.workdir.resolve();m=json.loads((D/'clip-map.json').read_text());clips=m['clips'];N=len(clips)
 fps=Fraction(m['fps_numerator'],m['fps_denominator']) if 'fps_numerator' in m else Fraction(str(m['fps'])).limit_denominator(1001000)
 timebase=m.get('timebase',round(float(fps)));review=json.loads(a.reviewed.read_text())
 ids={str(c['clip']) for c in clips}
 if set(review)!=ids:raise ValueError('Reviewed text must cover exactly the retained clip numbers')
 for n,r in review.items():
  if not isinstance(r,dict) or not isinstance(r.get('text'),str) or not r['text'].strip():raise ValueError(f'Missing reviewed text for clip {n}')
  if not isinstance(r.get('uncertainties',[]),list):raise ValueError('uncertainties must be a list of strings')
 if 'manifest' in m:
  original=Path(m['manifest']);assert hashlib.sha256(original.read_bytes()).hexdigest()==m['manifest_sha256'],'Manifest changed; reprepare/review'
  source_clips=json.loads(original.read_text())['clips']
  assert len(source_clips)==N
  for x,y in zip(source_clips,clips):
   for k in ['clip','source_in','source_out','timeline_in','timeline_out']:assert x[k]==y[k]
 def tc(fr):
  sec,ff=divmod(fr,timebase);minute,ss=divmod(sec,60);hh,mm=divmod(minute,60)
  return f'{hh:02}:{mm:02}:{ss:02}:{ff:02}'
 def stamp(fr):
  ms=round(Fraction(fr,1)/fps*1000);sec,ms=divmod(ms,1000);minute,ss=divmod(sec,60);hh,mm=divmod(minute,60)
  return f'{hh:02}:{mm:02}:{ss:02}.{ms:03}'
 out=D/'clips';out.mkdir(exist_ok=True);expected={f'clip-{c["clip"]:03}.txt' for c in clips}
 if {f.name for f in out.glob('clip-*.txt')}-expected:raise ValueError('Stale transcripts present; use a fresh output folder')
 rows=[];texts=[];audit=[]
 for c in clips:
  n=c['clip'];r=review[str(n)];text=r['text'].strip();notes=r.get('uncertainties',[])
  body=f'Clip {n:03} / {N}\nSource: {tc(c["source_in"])} → {tc(c["source_out"])}\nPremiere timeline: {tc(c["timeline_in"])} → {tc(c["timeline_out"])}\nTimecode: HH:MM:SS:FF, nominal {timebase} NDF; actual rate {fps} fps. End exclusive.\n\n{text}\n'
  f=out/f'clip-{n:03}.txt';f.write_text(body,encoding='utf-8');texts.append(body)
  row={'clip':n,'file':f'clips/{f.name}'}
  for k in ['source_in','source_out','timeline_in','timeline_out']:
   row[k+'_timecode']=tc(c[k]);row[k+'_time']=stamp(c[k]);row[k+'_frame']=c[k]
  row['review_note']='; '.join(notes);rows.append(row)
  audit.append({'clip':n,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'review_reason':r.get('reason',''),'uncertainties':notes})
 with (D/'Clip Index.csv').open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 (D/'All Talking Clips.txt').write_text(('\n'+'='*72+'\n\n').join(texts),encoding='utf-8')
 (D/'Read Me.txt').write_text(f'{N} separate transcripts match the retained clips in the supplied cut manifest.\nSource: {m["source"]}\nTimecode HH:MM:SS:FF is frames, nominal {timebase} NDF, actual rate {fps} fps. End points are exclusive. CSV also contains real-time milliseconds and frame indices.\nClip boundaries are exact edit ranges; recognition word timings are approximate. Repetitions and incomplete takes should be preserved by the review. Unclear wording is marked [غير واضح] and/or noted in the CSV.\nThese are reviewed machine transcripts, not certified or guaranteed 100%-accurate human transcription.\n',encoding='utf-8')
 archive=D/'Talking Clip Transcripts.zip';files=[D/'Read Me.txt',D/'Clip Index.csv',D/'All Talking Clips.txt',*sorted(out.glob('clip-*.txt'))]
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
  for f in files:z.write(f,f.relative_to(D))
 with zipfile.ZipFile(archive) as z:
  assert z.testzip() is None and len(z.namelist())==N+3
  for f in files:assert z.read(str(f.relative_to(D)))==f.read_bytes()
 verification={'clips':N,'files':N,'archive_files':N+3,'all_nonempty':True,'archive_integrity':'passed','timeline_frames':clips[-1]['timeline_out'],'timeline_seconds':float(clips[-1]['timeline_out']/fps),'note_clips':[c['clip'] for c in clips if review[str(c['clip'])].get('uncertainties')],'transcripts':audit}
 (D/'transcript-verification.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in verification.items() if k!='transcripts'}))
if __name__=='__main__':main()
