from pathlib import Path
import json,csv,xml.etree.ElementTree as E,hashlib,argparse,re
from fractions import Fraction
P=argparse.ArgumentParser(description="Build an editable Premiere XML and complete source/timeline reports")
P.add_argument('--workdir',required=True,type=Path);args=P.parse_args()
D=args.workdir.expanduser().resolve();s=json.loads((D/'cuts.json').read_text());N=s['source_frames']
fps=Fraction(s['fps_numerator'],s['fps_denominator']);timebase=s['timebase'];channels=s['audio_channels']
source=Path(s['source']);clips=s['clips'];total=s['timeline_frames'];name=s['sequence_name']
if not clips:raise ValueError('No retained clips: review detection before creating a sequence')
filename=re.sub(r'[^\w .-]','_',name).strip() or 'Speech Cuts'

def add(p,t,v=None,**attrs):
 e=E.SubElement(p,t,attrs)
 if v is not None:e.text=str(v)
 return e
def rate(p):
 r=add(p,'rate');add(r,'timebase',timebase);add(r,'ntsc','TRUE' if s['ntsc'] else 'FALSE')
def video_format(p):
 c=add(p,'samplecharacteristics');rate(c)
 for k,v in [('width',s['width']),('height',s['height']),('anamorphic','FALSE'),('pixelaspectratio','square'),('fielddominance','none'),('colordepth',24)]:add(c,k,v)
def audio_format(p):
 c=add(p,'samplecharacteristics');add(c,'depth',16);add(c,'samplerate',s['audio_sample_rate'])
root=E.Element('xmeml',version='5');seq=add(root,'sequence',id='EA-Speech-Cuts');add(seq,'name',name);add(seq,'duration',total);rate(seq);add(seq,'in',-1);add(seq,'out',-1)
tc=add(seq,'timecode');rate(tc);add(tc,'string','00:00:00:00');add(tc,'frame',0);add(tc,'displayformat','NDF')
media=add(seq,'media');video=add(media,'video');video_format(add(video,'format'));vt=add(video,'track');audio=add(media,'audio');add(audio,'numOutputChannels',channels);audio_format(add(audio,'format'))
outputs=add(audio,'outputs');group=add(outputs,'group');add(group,'index',1);add(group,'numchannels',channels);add(group,'downmix',0)
for channel in range(1,channels+1):add(add(group,'channel'),'index',channel)
audio_tracks=[add(audio,'track') for _ in range(channels)]
file_written=False
for row in clips:
 i=row['clip'];ids=[f'EA-clip-{i:03}-video',f'EA-clip-{i:03}-left',f'EA-clip-{i:03}-right']
 for kind,track,cid,index in [('video',vt,ids[0],1)]+[('audio',audio_tracks[j-1],ids[j],j) for j in range(1,channels+1)]:
  ci=add(track,'clipitem',id=cid);add(ci,'name',f'Clip {i:03}');add(ci,'enabled','TRUE');add(ci,'duration',N);rate(ci)
  for key,val in [('start',row['timeline_in']),('end',row['timeline_out']),('in',row['source_in']),('out',row['source_out'])]:add(ci,key,val)
  if kind=='video':add(ci,'anamorphic','FALSE');add(ci,'pixelaspectratio','square')
  f=add(ci,'file',id='EA-Original-Media')
  if not file_written:
   add(f,'name',source.name);add(f,'pathurl',source.as_uri().replace('file:///','file://localhost/'));rate(f);add(f,'duration',N)
   ftc=add(f,'timecode');rate(ftc);add(ftc,'string','00:00:00:00');add(ftc,'frame',0);add(ftc,'displayformat','NDF')
   fm=add(f,'media');fv=add(fm,'video');add(fv,'duration',N);video_format(fv);fa=add(fm,'audio');audio_format(fa);add(fa,'channelcount',channels);add(fa,'layout','stereo' if channels==2 else 'mono');file_written=True
  st=add(ci,'sourcetrack');add(st,'mediatype',kind);add(st,'trackindex',index)
  for linkid,typ,track_index in [(ids[0],'video',1)]+[(ids[j],'audio',j) for j in range(1,channels+1)]:
   link=add(ci,'link');add(link,'linkclipref',linkid);add(link,'mediatype',typ);add(link,'trackindex',track_index);add(link,'clipindex',i)
   if typ=='audio' and channels==2:add(link,'groupindex',1)
for tr in [vt,*audio_tracks]:add(tr,'enabled','TRUE');add(tr,'locked','FALSE')
for i,tr in enumerate(audio_tracks,1):add(tr,'outputchannelindex',i)
E.indent(root);xml=D/(filename+'.xml');xml.write_text('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE xmeml>\n'+E.tostring(root,encoding='unicode')+'\n')
def timecode(fr):
 seconds,ff=divmod(fr,timebase);minutes,ss=divmod(seconds,60);hh,mm=divmod(minutes,60);return f'{hh:02}:{mm:02}:{ss:02}:{ff:02}'
def stamp(fr):
 ms=round(fr/fps*1000);seconds,milli=divmod(ms,1000);minutes,ss=divmod(seconds,60);hh,mm=divmod(minutes,60);return f'{hh:02}:{mm:02}:{ss:02}.{milli:03}'
rows=[]
for c in clips:rows.append({'kind':'Clip','number':c['clip'],'source_in':c['source_in'],'source_out':c['source_out'],'timeline_in':c['timeline_in'],'timeline_out':c['timeline_out']})
for c in s['removed']:rows.append({'kind':'No talk','number':c['no_talk'],'source_in':c['source_in'],'source_out':c['source_out'],'timeline_in':None,'timeline_out':None})
rows.sort(key=lambda x:x['source_in'])
lines=[name.upper(),'',f'Original: {source}','Premiere project: save the imported sequence as a .prproj',f'Sequence: {name}',f'Original duration: {stamp(N)}',f'Edited duration: {stamp(total)}',f'Removed: {stamp(N-total)} in {len(s["removed"])} no-talking intervals',f'Kept clips: {len(clips)}','',
 'Times below refer to the ORIGINAL recording. End times are exclusive.',
 f'Format HH:MM:SS.mmm. Frame timecode HH:MM:SS:FF, nominal {timebase}, NDF; actual rate {fps} fps.',
 'No talk means the removed part of a detected pause; speech margins remain in adjacent clips.',
 f"Pause detection: at least {s['settings']['minimum_no_talk_seconds']:.2f} s; retain {s['settings']['speech_tail_padding_seconds']:.2f} s after and {s['settings']['speech_start_padding_seconds']:.2f} s before speech.",
 f'Cuts only: original framing, image, {channels} audio channel(s) and speed.','', 'ORIGINAL RECORDING - EVERY KEPT CLIP AND REMOVED PAUSE','']
for row in rows:lines.append(f'{row["kind"]} {row["number"]}: {stamp(row["source_in"])} to {stamp(row["source_out"])}')
lines+=['','EDITED PREMIERE TIMELINE - KEPT CLIPS','']
for c in clips:lines.append(f'Clip {c["clip"]}: {stamp(c["timeline_in"])} to {stamp(c["timeline_out"])} | source {stamp(c["source_in"])} to {stamp(c["source_out"])} | Premiere {timecode(c["timeline_in"])} to {timecode(c["timeline_out"])}')
(D/'Cut Report.txt').write_text('\n'.join(lines)+'\n')
with (D/'Cut Report.csv').open('w',newline='',encoding='utf-8-sig') as f:
 fields=['type','number','source_start','source_end_exclusive','duration','timeline_start','timeline_end_exclusive','source_start_timecode','source_end_timecode','timeline_start_timecode','timeline_end_timecode','source_in_frame','source_out_frame']
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
 for r in rows:
  present=r['timeline_in'] is not None
  w.writerow({'type':r['kind'],'number':r['number'],'source_start':stamp(r['source_in']),'source_end_exclusive':stamp(r['source_out']),'duration':stamp(r['source_out']-r['source_in']),'timeline_start':stamp(r['timeline_in']) if present else '', 'timeline_end_exclusive':stamp(r['timeline_out']) if present else '', 'source_start_timecode':timecode(r['source_in']),'source_end_timecode':timecode(r['source_out']),'timeline_start_timecode':timecode(r['timeline_in']) if present else '', 'timeline_end_timecode':timecode(r['timeline_out']) if present else '', 'source_in_frame':r['source_in'],'source_out_frame':r['source_out']})
# Validate complete source coverage, frame-accurate A/V alignment, and no timeline gaps.
assert rows[0]['source_in']==0 and rows[-1]['source_out']==N
assert all(a['source_out']==b['source_in'] for a,b in zip(rows,rows[1:]))
parsed=E.parse(xml);tracks=parsed.findall('./sequence/media/video/track')+parsed.findall('./sequence/media/audio/track')
for tr in tracks:
 cursor=0
 for ci,c in zip(tr.findall('clipitem'),clips):
  assert int(ci.findtext('start'))==cursor
  assert int(ci.findtext('end'))-cursor==int(ci.findtext('out'))-int(ci.findtext('in'))
  assert (int(ci.findtext('in')),int(ci.findtext('out')))==(c['source_in'],c['source_out'])
  cursor=int(ci.findtext('end'))
 assert len(tr.findall('clipitem'))==len(clips) and cursor==total
verification={'source_coverage_frames':N,'kept_frames':total,'removed_frames':N-total,'edited_duration_timecode':timecode(total),'kept_clips_per_track':len(clips),'tracks':['V1']+[f'A{j}' for j in range(1,channels+1)],'all_tracks_aligned':True,'no_sequence_gaps':True,'source_untouched_sha256':s['source_sha256'],'xml_sha256':hashlib.sha256(xml.read_bytes()).hexdigest(),'native_premiere_import_verified':False,'sequence_name':name,'xml_file':str(xml)}
(D/'verification.json').write_text(json.dumps(verification,indent=2));print(json.dumps(verification,indent=2));print('\n'.join(lines[:25]))
