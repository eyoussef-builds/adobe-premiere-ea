"""Synthetic integration checks; no private footage, ML downloads or Adobe needed."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import wave
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'skills' / 'adobe-premiere-ea' / 'scripts'


@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'FFmpeg/FFprobe required')
class HelperIntegration(unittest.TestCase):
    def run_helper(self, name, *args, success=True):
        result = subprocess.run([sys.executable, str(SCRIPTS / name), *map(str, args)],
                                capture_output=True, text=True)
        if success:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0)
        return result

    def test_manifest_xml_audio_and_archive(self):
        with tempfile.TemporaryDirectory() as tmp:
            task = Path(tmp)
            source = task / 'synthetic.mov'
            subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-f', 'lavfi',
                            '-i', 'color=c=blue:s=160x90:r=30:d=3', '-f', 'lavfi',
                            '-i', 'sine=frequency=440:sample_rate=48000:duration=3',
                            '-ac', '2', '-c:v', 'mpeg4', '-c:a', 'pcm_s16le',
                            '-shortest', str(source)], check=True)
            cuts = task / 'cuts'
            cuts.mkdir()
            clips = [dict(clip=1, source_in=0, source_out=30, timeline_in=0, timeline_out=30),
                     dict(clip=2, source_in=60, source_out=90, timeline_in=30, timeline_out=60)]
            manifest = dict(source=str(source), source_frames=90, timeline_frames=60,
                            fps=30, fps_numerator=30, fps_denominator=1, timebase=30,
                            ntsc=False, width=160, height=90, audio_channels=2,
                            audio_sample_rate=48000, sequence_name='Synthetic Cuts',
                            source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                            clips=clips, removed=[dict(no_talk=1, source_in=30, source_out=60)],
                            settings=dict(minimum_no_talk_seconds=.5,
                                          speech_tail_padding_seconds=.2,
                                          speech_start_padding_seconds=.15))
            path = cuts / 'cuts.json'
            path.write_text(json.dumps(manifest))
            self.run_helper('build_sequence.py', '--workdir', cuts)
            xml = ET.parse(cuts / 'Synthetic Cuts.xml')
            tracks = xml.findall('./sequence/media/video/track') + xml.findall('./sequence/media/audio/track')
            self.assertEqual(len(tracks), 3)
            for track in tracks:
                items = track.findall('clipitem')
                self.assertEqual(len(items), 2)
                self.assertEqual([tuple(int(c.findtext(k)) for k in ('start','end','in','out')) for c in items],
                                 [(0,30,0,30), (30,60,60,90)])
                self.assertTrue(all(len(c.findall('link')) == 3 for c in items))
            self.assertEqual([t.findtext('outputchannelindex') for t in tracks[1:]], ['1','2'])
            transcripts = task / 'transcripts'
            self.run_helper('prepare_transcripts.py', '--manifest', path, '--output-dir', transcripts)
            with wave.open(str(transcripts / 'edited-speech-analysis.wav')) as audio:
                self.assertEqual((audio.getframerate(), audio.getnframes()), (16000,32000))
            reviewed = transcripts / 'reviewed.json'
            reviewed.write_text(json.dumps({'1':dict(text='Synthetic first clip.',uncertainties=[]),
                                             '2':dict(text='Synthetic second clip.',uncertainties=[])}))
            self.run_helper('package_transcripts.py', '--workdir', transcripts, '--reviewed', reviewed)
            with zipfile.ZipFile(transcripts / 'Talking Clip Transcripts.zip') as archive:
                self.assertIsNone(archive.testzip())
                self.assertEqual(len(archive.namelist()), 5)
                self.assertTrue(all(not n.endswith(('.wav','.mov')) for n in archive.namelist()))
            scope = task / 'scope.json'
            scope.write_text(json.dumps(dict(source=str(source), active_clip_numbers=[1,2],
                                             active_clips=[dict(**c,text='Synthetic speech.') for c in clips])))
            plan = task / 'plan.json'
            option = dict(slug='reversed',name='Reversed',intent='Synthetic reorder',script_anchor='Synthetic',
                          beats=[dict(label='Example',clips=[dict(clip=2),dict(clip=1)])])
            plan.write_text(json.dumps(dict(source=str(source), options=[option])))
            output = task / 'options'
            self.run_helper('build_options.py','--manifest',path,'--active-scope',scope,'--plan',plan,'--output-dir',output)
            ordered = json.loads((output / 'reversed' / 'cuts.json').read_text())['clips']
            self.assertEqual([c['clip'] for c in ordered], [2,1])
            self.assertEqual([c['timeline_in'] for c in ordered], [0,30])
            option['beats'][0]['clips'] = [dict(clip=3)]
            plan.write_text(json.dumps(dict(source=str(source), options=[option])))
            self.run_helper('build_options.py','--manifest',path,'--active-scope',scope,'--plan',plan,
                            '--output-dir',task/'rejected',success=False)
            # Packaging must refuse stale maps after edit boundaries change.
            manifest['clips'][0]['source_out'] = 29
            path.write_text(json.dumps(manifest))
            self.run_helper('package_transcripts.py','--workdir',transcripts,'--reviewed',reviewed,success=False)


if __name__ == '__main__':
    unittest.main()
