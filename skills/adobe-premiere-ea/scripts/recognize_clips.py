"""Resumable Qwen per-clip or Whisper grouped/individual local recognition."""
import argparse,dataclasses,gc,hashlib,json,os,time,wave
from pathlib import Path

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--workdir',required=True,type=Path);p.add_argument('--backend',choices=['qwen','whisper'],required=True)
 p.add_argument('--model',required=True,type=Path);p.add_argument('--run',required=True)
 p.add_argument('--language',required=True,help='Qwen: Arabic; Whisper: ar (adapt for other languages)')
 p.add_argument('--clips',default='',help='Comma-separated targeted clip numbers; forces individual recognition')
 p.add_argument('--group-seconds',type=float,default=120,help='Whisper only; 0 means individual clips')
 p.add_argument('--max-items',type=int);a=p.parse_args()
 D=a.workdir.resolve();model_path=a.model.resolve()
 if not model_path.is_dir():raise ValueError('Download the model first and pass its local directory')
 if Path(a.run).name!=a.run:raise ValueError('Run name must be a directory name')
 os.environ.setdefault('HF_HOME',str(D/'.cache/huggingface'));os.environ['HF_HUB_OFFLINE']='1'
 import numpy as np
 import mlx.core as mx
 mapping=json.loads((D/'clip-map.json').read_text());sr=mapping['sample_rate'];clips=mapping['clips']
 selected=set(map(int,a.clips.split(','))) if a.clips else None
 if selected and not selected.issubset({c['clip'] for c in clips}):raise ValueError('Unknown clip number')
 groups=[];current=[]
 for c in clips:
  if selected and c['clip'] not in selected:continue
  individual=a.backend=='qwen' or selected or a.group_seconds<=0
  if current and (individual or c['edited_audio_end']-current[0]['edited_audio_start']>a.group_seconds):groups.append(current);current=[]
  current.append(c)
 if current:groups.append(current)
 out=D/'raw'/a.run;out.mkdir(parents=True,exist_ok=True)
 settings={'backend':a.backend,'model':str(model_path),'model_config_sha256':hashlib.sha256((model_path/'config.json').read_bytes()).hexdigest(),'language':a.language,'map_sha256':hashlib.sha256((D/'clip-map.json').read_bytes()).hexdigest(),'group_seconds':a.group_seconds,'clips':a.clips,'recipe_version':1}
 meta=out/'run.json'
 if meta.exists() and json.loads(meta.read_text())!=settings:raise ValueError('Run settings changed; choose a new run name')
 meta.write_text(json.dumps(settings,indent=2))
 audio_file=D/'edited-speech-analysis.wav'
 if mapping.get('audio_sha256') and hashlib.sha256(audio_file.read_bytes()).hexdigest()!=mapping['audio_sha256']:raise ValueError('Prepared audio changed; reprepare in a fresh folder')
 with wave.open(str(audio_file)) as w:
  assert w.getframerate()==sr and w.getnchannels()==1 and w.getsampwidth()==2
  audio=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
 assert len(audio)==mapping['edited_samples']
 mx.set_cache_limit(128*1024**2);mx.set_memory_limit(5*1024**3);mx.random.seed(0)
 if a.backend=='qwen':
  from mlx_audio.stt import load
  model=load(str(model_path))
 else:import mlx_whisper
 completed=0
 for i,cs in enumerate(groups,1):
  if a.max_items and i>a.max_items:break
  grouped=a.backend=='whisper' and not selected and a.group_seconds>0
  f=out/(f'group-{i:03}.json' if grouped else f'clip-{cs[0]["clip"]:03}.json')
  if f.exists():completed+=1;continue
  lo=cs[0]['edited_audio_in_sample'];hi=cs[-1]['edited_audio_out_sample'];offset=lo/sr
  print(json.dumps({'item':i,'total':len(groups),'clips':[c['clip'] for c in cs]}),flush=True);stamp=time.time()
  if a.backend=='qwen':
   duration=(hi-lo)/sr
   result=model.generate(audio[lo:hi],language=a.language,max_tokens=max(2048,int(duration*30)),temperature=0.,verbose=False,prefill_step_size=512)
   result=dataclasses.asdict(result)
  else:
   result=mlx_whisper.transcribe(audio[lo:hi],path_or_hf_repo=str(model_path),language=a.language,task='transcribe',verbose=None,temperature=(0.,.2,.4),best_of=3,word_timestamps=grouped,condition_on_previous_text=grouped,hallucination_silence_threshold=1.)
  for seg in result.get('segments',[]):
   seg['edited_start']=offset+seg['start'];seg['edited_end']=offset+seg['end']
   for word in seg.get('words',[]):word.update(edited_start=offset+word['start'],edited_end=offset+word['end'])
  result.update({'clip_numbers':[c['clip'] for c in cs],'edited_audio_offset':offset,'elapsed_seconds':time.time()-stamp,'model':str(model_path)})
  if not grouped:result['clip']=cs[0]['clip']
  f.write_text(json.dumps(result,ensure_ascii=False,indent=2,default=lambda x:x.item() if isinstance(x,np.generic) else str(x)))
  completed+=1
  print(result['text'],flush=True)
  (out/'progress.json').write_text(json.dumps({'items_complete':completed,'items_total':len(groups),'complete':completed==len(groups)}))
  del result;gc.collect();mx.clear_cache()
 print(json.dumps({'items_complete':completed,'items_total':len(groups),'complete':completed==len(groups)}))
if __name__=='__main__':main()
