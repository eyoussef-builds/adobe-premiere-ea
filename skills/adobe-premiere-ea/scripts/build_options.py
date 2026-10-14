"""Build reordered, linked Premiere XML options from an approved clip scope."""
import argparse,csv,hashlib,json,re,subprocess,xml.etree.ElementTree as E
from fractions import Fraction
from pathlib import Path

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--manifest',required=True,type=Path);p.add_argument('--active-scope',required=True,type=Path);p.add_argument('--plan',required=True,type=Path);p.add_argument('--output-dir',required=True,type=Path);p.add_argument('--ffprobe',default='ffprobe');a=p.parse_args()
 base=json.loads(a.manifest.read_text());scope=json.loads(a.active_scope.read_text());plan=json.loads(a.plan.read_text());D=a.output_dir.resolve();D.mkdir(parents=True,exist_ok=True)
 source=Path(base['source']).resolve();assert source==Path(scope['source']).resolve()==Path(plan['source']).resolve()
 fps=Fraction(base['fps_numerator'],base['fps_denominator']) if 'fps_numerator' in base else Fraction(str(base['fps'])).limit_denominator(1001000)
 probe=json.loads(subprocess.check_output([a.ffprobe,'-v','error','-show_streams','-of','json',str(source)]));v=next(s for s in probe['streams'] if s['codec_type']=='video');au=next(s for s in probe['streams'] if s['codec_type']=='audio');channels=au['channels'];sample_rate=int(au['sample_rate'])
 assert channels in [1,2],'Adapt audio routing for more than two channels'
 assert Fraction(v['r_frame_rate'])==fps==Fraction(v['avg_frame_rate']),'Only matched CFR source supported'
 source_hash=hashlib.file_digest(source.open('rb'),'sha256').hexdigest();timebase=base.get('timebase',round(float(fps)));ntsc=fps.denominator!=1
 assert not ntsc or fps in [Fraction(24000,1001),Fraction(30000,1001),Fraction(60000,1001)],'Adapt unsupported fractional rates'
 allowed=set(scope['active_clip_numbers']);byid={c['clip']:c for c in base['clips']}
 for c in scope['active_clips']:
  for k in ['source_in','source_out']:assert c[k]==byid[c['clip']][k]
 texts={c['clip']:c['text'] for c in scope['active_clips']}
 root=E.Element('xmeml',version='5');bin=E.SubElement(root,'bin');E.SubElement(bin,'name').text=plan.get('bin_name','Sequence Options');children=E.SubElement(bin,'children')
 def add(p,t,value=None,**attrs):
  el=E.SubElement(p,t,attrs)
  if value is not None:el.text=str(value)
  return el
 def rate(p):
  r=add(p,'rate');add(r,'timebase',timebase);add(r,'ntsc','TRUE' if ntsc else 'FALSE')
 def vf(p):
  c=add(p,'samplecharacteristics');rate(c)
  for k,value in [('width',v['width']),('height',v['height']),('anamorphic','FALSE'),('pixelaspectratio','square'),('fielddominance','none'),('colordepth',24)]:add(c,k,value)
 def af(p):
  c=add(p,'samplecharacteristics');add(c,'depth',16);add(c,'samplerate',sample_rate)
 def tc(fr):
  seconds,ff=divmod(fr,timebase);minutes,ss=divmod(seconds,60);hh,mm=divmod(minutes,60);return f'{hh:02}:{mm:02}:{ss:02}:{ff:02}'
 names=set();slugs=set();summaries=[]
 for oi,option in enumerate(plan['options'],1):
  slug=option['slug'];name=option['name'];assert re.fullmatch('[a-z0-9-]+',slug) and slug not in slugs and name not in names
  slugs.add(slug);names.add(name);folder=D/slug;folder.mkdir(exist_ok=True);cursor=0;clips=[];beats=[];prefix=f'EA-option-{oi}'
  for bi,beat in enumerate(option['beats'],1):
   start=cursor
   for entry in beat['clips']:
    n=entry['clip'];assert n in allowed,f'Clip{n} is excluded from active scope'
    parent=byid[n];lo=entry.get('source_in',parent['source_in']);hi=entry.get('source_out',parent['source_out'])
    assert isinstance(lo,int) and isinstance(hi,int) and parent['source_in']<=lo<hi<=parent['source_out']
    if (lo,hi)!=(parent['source_in'],parent['source_out']):assert entry.get('text'),'Supply actual trim text, not the full-parent transcript'
    clips.append({'segment':len(clips)+1,'clip':n,'source_in':lo,'source_out':hi,'timeline_in':cursor,'timeline_out':cursor+hi-lo,'beat':beat['label'],'text':entry.get('text',texts[n])});cursor+=hi-lo
   beats.append({'beat':bi,'label':beat['label'],'timeline_in':start,'timeline_out':cursor})
  assert clips,'Empty option'
  # No overlapping reused footage within one option; variants may share clips.
  ranges=sorted((c['source_in'],c['source_out']) for c in clips)
  assert all(x[1]<=y[0] for x,y in zip(ranges,ranges[1:])),'An option reuses overlapping footage'
  seq=add(children,'sequence',id=prefix);add(seq,'name',name);add(seq,'duration',cursor);rate(seq);add(seq,'in',-1);add(seq,'out',-1)
  t=add(seq,'timecode');rate(t);add(t,'string','00:00:00:00');add(t,'frame',0);add(t,'displayformat','NDF')
  media=add(seq,'media');video=add(media,'video');vf(add(video,'format'));vt=add(video,'track');audio=add(media,'audio');add(audio,'numOutputChannels',channels);af(add(audio,'format'))
  g=add(add(audio,'outputs'),'group');add(g,'index',1);add(g,'numchannels',channels);add(g,'downmix',0)
  for j in range(1,channels+1):add(add(g,'channel'),'index',j)
  ats=[add(audio,'track') for _ in range(channels)];file_written=False;fileid=prefix+'-source'
  for c in clips:
   ordinal=c['segment'];ids=[f'{prefix}-{ordinal:03}-v',*[f'{prefix}-{ordinal:03}-a{j}' for j in range(1,channels+1)]]
   for kind,tr,cid,index in [('video',vt,ids[0],1)]+[('audio',ats[j-1],ids[j],j) for j in range(1,channels+1)]:
    ci=add(tr,'clipitem',id=cid);add(ci,'name',f'Clip {c["clip"]:03} | {c["beat"]}');add(ci,'enabled','TRUE');add(ci,'duration',base['source_frames']);rate(ci)
    for k,key in [('start','timeline_in'),('end','timeline_out'),('in','source_in'),('out','source_out')]:add(ci,k,c[key])
    if kind=='video':add(ci,'anamorphic','FALSE');add(ci,'pixelaspectratio','square')
    f=add(ci,'file',id=fileid)
    if not file_written:
     add(f,'name',source.name);add(f,'pathurl',source.as_uri().replace('file:///','file://localhost/'));rate(f);add(f,'duration',base['source_frames']);ft=add(f,'timecode');rate(ft);add(ft,'string','00:00:00:00');add(ft,'frame',0);add(ft,'displayformat','NDF');fm=add(f,'media');fv=add(fm,'video');add(fv,'duration',base['source_frames']);vf(fv);fa=add(fm,'audio');af(fa);add(fa,'channelcount',channels);add(fa,'layout','stereo' if channels==2 else 'mono');file_written=True
    st=add(ci,'sourcetrack');add(st,'mediatype',kind);add(st,'trackindex',index)
    for linkid,typ,ti in [(ids[0],'video',1)]+[(ids[j],'audio',j) for j in range(1,channels+1)]:
     link=add(ci,'link');add(link,'linkclipref',linkid);add(link,'mediatype',typ);add(link,'trackindex',ti);add(link,'clipindex',ordinal)
     if typ=='audio' and channels==2:add(link,'groupindex',1)
  for tr in [vt,*ats]:add(tr,'enabled','TRUE');add(tr,'locked','FALSE')
  for j,tr in enumerate(ats,1):add(tr,'outputchannelindex',j)
  # Check generated source, timeline and A/V links, independently of file serialization.
  tracks=[vt,*ats]
  for tr in tracks:
   items=tr.findall('clipitem');assert len(items)==len(clips)
   for ci,c in zip(items,clips):
    assert tuple(int(ci.findtext(k)) for k in ['start','end','in','out'])==tuple(c[k] for k in ['timeline_in','timeline_out','source_in','source_out'])
    assert len(ci.findall('link'))==channels+1
  manifest={**base,'source':str(source),'source_sha256':source_hash,'fps_numerator':fps.numerator,'fps_denominator':fps.denominator,'timebase':timebase,'audio_channels':channels,'audio_sample_rate':sample_rate,'sequence_name':name,'timeline_frames':cursor,'timeline_seconds':float(cursor/fps),'clips':clips,'removed':[],'beats':beats,'editorial_intent':option['intent'],'active_scope':str(a.active_scope.resolve())}
  (folder/'cuts.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
  (folder/'verification.json').write_text(json.dumps({'xml_tracks_aligned':True,'no_sequence_gaps':True,'active_scope_enforced':True,'native_premiere_import_verified':False},indent=2))
  with (folder/'Sequence Map.csv').open('w',encoding='utf-8-sig',newline='') as f:
   fields=['segment','original_clip','beat','timeline_start','timeline_end_exclusive','source_start','source_end_exclusive','text'];w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
   for c in clips:w.writerow({'segment':c['segment'],'original_clip':c['clip'],'beat':c['beat'],'timeline_start':tc(c['timeline_in']),'timeline_end_exclusive':tc(c['timeline_out']),'source_start':tc(c['source_in']),'source_end_exclusive':tc(c['source_out']),'text':c['text']})
  lines=[name,f'Duration: {tc(cursor)} (nominal{timebase}NDF, actual{fps}fps)',f'Script guide: {option["script_anchor"]}',f'Intent: {option["intent"]}','', 'ORDERED TALKING FOOTAGE — NO ADDED MATERIAL','']
  for b in beats:
   lines.extend([f'{tc(b["timeline_in"])} to {tc(b["timeline_out"])} | {b["label"]}'])
   for c in clips:
    if c['beat']==b['label']:lines.extend([f'Clip{c["clip"]:03} | source{tc(c["source_in"])} to{tc(c["source_out"])}',c['text']])
   lines.append('')
  (folder/'Sequence Script.txt').write_text('\n'.join(lines),encoding='utf-8')
  summaries.append({'name':name,'slug':slug,'duration_timecode':tc(cursor),'seconds':float(cursor/fps),'segments':len(clips),'script_anchor':option['script_anchor'],'recommended':option.get('recommended',False),'intent':option['intent'],'original_clip_order':[c['clip'] for c in clips]})
 E.indent(root);filename=plan.get('xml_filename','Combined Sequence Options.xml');assert Path(filename).name==filename and filename.endswith('.xml');xml=D/filename;xml.write_text('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE xmeml>\n'+E.tostring(root,encoding='unicode')+'\n')
 E.parse(xml)
 (D/'options-summary.json').write_text(json.dumps(summaries,ensure_ascii=False,indent=2));print(json.dumps(summaries,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
