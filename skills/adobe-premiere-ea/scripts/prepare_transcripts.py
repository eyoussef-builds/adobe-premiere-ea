"""Prepare local 16 kHz analysis audio and a sample/frame map from cuts.json."""
import argparse,hashlib,json,shutil,subprocess,wave
from fractions import Fraction
from pathlib import Path

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--manifest',required=True,type=Path);p.add_argument('--output-dir',required=True,type=Path)
 p.add_argument('--audio',type=Path,help='Existing source-aligned mono PCM16 16kHz analysis WAV')
 p.add_argument('--ffmpeg',default='ffmpeg');a=p.parse_args()
 manifest=a.manifest.resolve();s=json.loads(manifest.read_text());out=a.output_dir.resolve()
 if (out/'clip-map.json').exists():raise ValueError('Already prepared; reuse the existing map or choose a fresh output directory')
 fps=Fraction(s['fps_numerator'],s['fps_denominator']) if 'fps_numerator' in s else Fraction(str(s['fps'])).limit_denominator(1001000)
 clips=s['clips'];assert clips,'No retained clips'
 cursor=0;previous=0;ids=set()
 for c in clips:
  assert c['clip'] not in ids;ids.add(c['clip'])
  assert previous<=c['source_in']<c['source_out']<=s['source_frames']
  assert c['timeline_in']==cursor and c['source_out']-c['source_in']==c['timeline_out']-cursor
  previous=c['source_out'];cursor=c['timeline_out']
 assert cursor==s['timeline_frames']
 out.mkdir(parents=True,exist_ok=True)
 audio=a.audio.resolve() if a.audio else out/'original-analysis.wav'
 if not a.audio:
  subprocess.run([a.ffmpeg,'-nostdin','-v','error','-n','-i',s['source'],'-map','0:a:0','-ac','1','-ar','16000','-c:a','pcm_s16le',str(audio)],check=True)
 with wave.open(str(audio)) as w:
  assert (w.getnchannels(),w.getsampwidth(),w.getframerate())==(1,2,16000),'Analysis audio must be mono PCM16 at16kHz'
  n=w.getnframes();raw=w.readframes(n)
 sr=16000;sample_cursor=0;mapped=[]
 stitched=out/'edited-speech-analysis.wav'
 with wave.open(str(stitched),'wb') as w:
  w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr)
  for c in clips:
   lo=round(Fraction(c['source_in'],1)/fps*sr);hi=round(Fraction(c['source_out'],1)/fps*sr)
   assert 0<=lo<hi<=n,('Source-aligned audio does not cover clip',c['clip'])
   w.writeframesraw(raw[lo*2:hi*2]);end=sample_cursor+hi-lo
   mapped.append({**c,'edited_audio_in_sample':sample_cursor,'edited_audio_out_sample':end,'edited_audio_start':sample_cursor/sr,'edited_audio_end':end/sr,'source_start':float(c['source_in']/fps),'source_end':float(c['source_out']/fps)})
   sample_cursor=end
 result={'source':s['source'],'manifest':str(manifest),'manifest_sha256':hashlib.sha256(manifest.read_bytes()).hexdigest(),'fps':float(fps),'fps_numerator':fps.numerator,'fps_denominator':fps.denominator,'timebase':s.get('timebase',round(float(fps))),'sample_rate':sr,'edited_samples':sample_cursor,'edited_audio_seconds':sample_cursor/sr,'audio_sha256':hashlib.sha256(stitched.read_bytes()).hexdigest(),'clips':mapped}
 (out/'clip-map.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
 print(json.dumps({'clips':len(clips),'seconds':sample_cursor/sr,'map':str(out/'clip-map.json')}))
if __name__=='__main__':main()
