"""Detect speech-protected cuts locally, quantized to the source frame rate."""
from pathlib import Path
import wave,json,time,math,argparse,subprocess,shutil,hashlib
from fractions import Fraction
P=argparse.ArgumentParser(description="Create frame-aligned speech-protected pause cuts locally")
P.add_argument('--input',required=True,type=Path);P.add_argument('--output-dir',required=True,type=Path)
P.add_argument('--sequence-name');P.add_argument('--min-pause',type=float,default=.50)
P.add_argument('--pre-speech',type=float,default=.15);P.add_argument('--post-speech',type=float,default=.20)
P.add_argument('--threshold',type=float,default=.25);P.add_argument('--negative-threshold',type=float,default=.10)
P.add_argument('--force',action='store_true');args=P.parse_args()
if min(args.min_pause,args.pre_speech,args.post_speech)<0:P.error('Pause and padding must be nonnegative')
if not 0<=args.negative_threshold<args.threshold<=1:P.error('Require 0 <= negative-threshold < threshold <= 1')
import numpy as np,torch
from silero_vad import load_silero_vad,get_speech_timestamps
from importlib.metadata import version
source=args.input.expanduser().resolve(strict=True);D=args.output_dir.expanduser().resolve()
if (D/'cuts.json').exists() and not args.force:P.error('Choose a fresh output directory, or explicitly use --force')
ffmpeg=shutil.which('ffmpeg');ffprobe=shutil.which('ffprobe')
if not ffmpeg or not ffprobe:P.error('ffmpeg and ffprobe must be on PATH')
probe=json.loads(subprocess.check_output([ffprobe,'-v','error','-show_streams','-show_format','-of','json',str(source)]))
v=next((x for x in probe['streams'] if x['codec_type']=='video'),None)
audio_stream=next((x for x in probe['streams'] if x['codec_type']=='audio'),None)
if not v or not audio_stream:P.error('Input must contain video and audio')
frame_rate=Fraction(v['avg_frame_rate'])
if frame_rate<=0 or frame_rate!=Fraction(v['r_frame_rate']):P.error('VFR/ambiguous frame rate: adapt the timing workflow before cutting')
timebase=round(float(frame_rate));ntsc=frame_rate.denominator!=1
if ntsc and frame_rate!=Fraction(timebase*1000,1001):P.error('Unsupported frame rate; adapt XML timing explicitly')
if v.get('field_order') not in (None,'unknown','progressive'):P.error('Interlaced footage needs an adapted workflow')
if v.get('sample_aspect_ratio','1:1') not in ('1:1','0:1','N/A'):P.error('Non-square pixels need explicit XML display mapping')
rotations=[x.get('rotation',0) for x in v.get('side_data_list',[])]
if any(float(x)%360 for x in rotations) or float(v.get('tags',{}).get('rotate','0'))%360:P.error('Rotated footage needs an orientation check')
if abs(float(v.get('start_time',0)))>.001 or abs(float(audio_stream.get('start_time',0)))>.001:P.error('Nonzero stream offsets require source/audio alignment')
channels=int(audio_stream['channels'])
if channels not in (1,2):P.error('Preserve multichannel input using an adapted channel mapping workflow')
source_frame_count=int(v['nb_frames']) if v.get('nb_frames','').isdigit() else 0
if not source_frame_count:
 count=json.loads(subprocess.check_output([ffprobe,'-v','error','-select_streams','v:0','-count_frames','-show_entries','stream=nb_read_frames','-of','json',str(source)]))
 source_frame_count=int(count['streams'][0]['nb_read_frames'])
if v.get('duration') and abs(float(v['duration'])-source_frame_count/float(frame_rate))>1.1/float(frame_rate):P.error('Frame count and duration disagree')
D.mkdir(parents=True,exist_ok=True)
subprocess.run([ffmpeg,'-v','error','-y','-i',str(source),'-map','0:a:0','-ac','1','-ar','16000','-c:a','pcm_s16le',str(D/'analysis-audio-16k.wav')],check=True)

with wave.open(str(D/'analysis-audio-16k.wav')) as w:
 rate=w.getframerate();audio=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
torch.set_num_threads(1);model=load_silero_vad();started=time.time();last=[-10]
def progress(v):
 if v-last[0]>=10:last[0]=v;print(f'Speech analysis {v:.0f}%',flush=True)
speech=get_speech_timestamps(torch.from_numpy(audio),model,sampling_rate=rate,threshold=args.threshold,neg_threshold=args.negative_threshold,min_speech_duration_ms=80,min_silence_duration_ms=100,speech_pad_ms=0,progress_tracking_callback=progress)
N=source_frame_count;fps=frame_rate;total=float(Fraction(N,1)/fps);raw=[{'start':x['start']/rate,'end':x['end']/rate} for x in speech]
if not raw:P.error('No speech detected; review the audio before making an all-deleted timeline')
gaps=[];cursor=0.
for row in raw:
 if row['start']>cursor:gaps.append((cursor,row['start']))
 cursor=max(cursor,row['end'])
if cursor<total:gaps.append((cursor,total))
removed=[]
for start,end in gaps:
 if end-start<args.min_pause:continue
 # Extra tail margin protects quiet/unvoiced word endings.
 a=start+(args.post_speech if start>0 else 0);b=end-(args.pre_speech if end<total-.05 else 0)
 lo=max(0,math.ceil(a*fps));hi=min(N,math.floor(b*fps))
 if hi-lo>=max(1,math.ceil(.10*fps)):removed.append({'source_in':lo,'source_out':hi,'raw_no_speech_start':start,'raw_no_speech_end':end})
kept=[];cursor=0;position=0
for row in removed+[{'source_in':N,'source_out':N}]:
 if row['source_in']>cursor:
  length=row['source_in']-cursor;kept.append({'clip':len(kept)+1,'source_in':cursor,'source_out':row['source_in'],'timeline_in':position,'timeline_out':position+length});position+=length
 cursor=row['source_out']
metrics=[]
for i,row in enumerate(removed):
 x=audio[min(len(audio),round(row['source_in']/fps*rate)):min(len(audio),round(row['source_out']/fps*rate))]
 rms=float(20*np.log10(np.sqrt(np.mean(x*x))+1e-10)) if len(x) else -200
 peak=float(20*np.log10(np.max(np.abs(x))+1e-10)) if len(x) else -200
 row.update({'no_talk':i+1,'rms_dbfs':round(rms,2),'peak_dbfs':round(peak,2)})
 if rms>-36:metrics.append(row)
result={'source':str(source),'source_frames':N,'fps':float(fps),'source_seconds':total,'timeline_frames':position,'timeline_seconds':position/fps,'removed_frames':N-position,'removed_seconds':(N-position)/fps,'clips':kept,'removed':removed,'raw_speech':raw,'settings':{'detector':'Silero VAD '+version('silero-vad')+' local CPU','threshold':args.threshold,'negative_threshold':args.negative_threshold,'minimum_no_talk_seconds':args.min_pause,'speech_tail_padding_seconds':args.post_speech,'speech_start_padding_seconds':args.pre_speech,'minimum_removed_frames':max(1,math.ceil(.1*fps)),'ranges':'start inclusive, end exclusive'},'higher_energy_removed_intervals_to_review':metrics,'elapsed_seconds':time.time()-started}
digest=hashlib.sha256()
with source.open('rb') as f:
 for block in iter(lambda:f.read(1024*1024),b''):digest.update(block)
result.update({'source_sha256':digest.hexdigest(),'fps_numerator':fps.numerator,'fps_denominator':fps.denominator,'timebase':timebase,'ntsc':ntsc,'width':int(v['width']),'height':int(v['height']),'audio_channels':channels,'audio_sample_rate':int(audio_stream['sample_rate']),'sequence_name':args.sequence_name or source.stem+' - Speech Cuts','timeline_seconds':float(position/fps),'removed_seconds':float((N-position)/fps)})
assert sum(x['source_out']-x['source_in'] for x in removed)+position==N
assert all(x['source_in']<x['source_out'] for x in kept)
(D/'cuts.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:result[k] for k in ('timeline_seconds','removed_seconds','elapsed_seconds')},indent=2),flush=True);print('Kept clips',len(kept),'removed pauses',len(removed),'higher-energy review',len(metrics),flush=True)
