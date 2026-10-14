#!/usr/bin/env python3
"""Read-only validation of a saved Premiere 26 project against cuts.json."""
import argparse
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as E


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--workdir', required=True, type=Path)
    p.add_argument('--project', required=True, type=Path)
    args = p.parse_args()
    work = args.workdir.expanduser().resolve()
    project = args.project.expanduser().resolve(strict=True)
    manifest = json.loads((work / 'cuts.json').read_text())
    data = project.read_bytes()
    root = E.fromstring(gzip.decompress(data) if data.startswith(b'\x1f\x8b') else data)
    by_id = {x.get('ObjectID'): x for x in root if x.get('ObjectID')}
    by_uid = {x.get('ObjectUID'): x for x in root if x.get('ObjectUID')}
    sequences = [x for x in root.findall('Sequence')
                 if x.get('ObjectUID') and x.findtext('Name') == manifest['sequence_name']]
    if len(sequences) != 1:
        raise ValueError('Expected one sequence matching the manifest name; inspect duplicates/schema')
    fps = Fraction(manifest['fps_numerator'], manifest['fps_denominator'])
    ticks_per_frame = Fraction(254016000000, 1) / fps
    details, audio_channels = [], []
    for group_ref in sequences[0].findall('./TrackGroups/TrackGroup/Second'):
        group = by_id[group_ref.get('ObjectRef')]
        if group.tag not in ('VideoTrackGroup', 'AudioTrackGroup'):
            continue
        for track_ref in group.findall('./TrackGroup/Tracks/Track'):
            track = by_uid[track_ref.get('ObjectURef')]
            refs = track.findall('./ClipTrack/ClipItems/TrackItems/TrackItem')
            if len(refs) != len(manifest['clips']):
                raise ValueError('Native clip count differs from the cut list')
            channel = None
            for ref, wanted in zip(refs, manifest['clips']):
                item = by_id[ref.get('ObjectRef')]
                timing = item.find('./ClipTrackItem/TrackItem')
                sub = by_id[item.find('./ClipTrackItem/SubClip').get('ObjectRef')]
                clip = by_id[sub.find('Clip').get('ObjectRef')]
                media_source = by_id[clip.find('./Clip/Source').get('ObjectRef')]
                media = by_uid[media_source.find('./MediaSource/Media').get('ObjectURef')]
                media_path = media.findtext('ActualMediaFilePath') or media.findtext('FilePath')
                if not media_path or Path(media_path).resolve() != Path(manifest['source']).resolve():
                    raise ValueError('Native clip references different media from the requested original')
                values = [timing.findtext('Start', '0'), timing.findtext('End'),
                          clip.findtext('./Clip/InPoint', '0'), clip.findtext('./Clip/OutPoint')]
                actual = tuple(Fraction(int(x), 1) / ticks_per_frame for x in values)
                expected = tuple(wanted[x] for x in ('timeline_in', 'timeline_out', 'source_in', 'source_out'))
                if actual != expected:
                    raise ValueError(f'Native timing mismatch for Clip {wanted["clip"]}: {actual} != {expected}')
                if group.tag == 'AudioTrackGroup':
                    secondary = by_id[clip.find('./SecondaryContents/SecondaryContentItem').get('ObjectRef')]
                    current = int(secondary.findtext('ChannelIndex', '0'))
                    if channel is not None and current != channel:
                        raise ValueError('Source audio channel changes within a track')
                    channel = current
            details.append({'type': track.tag, 'clips': len(refs), 'source_audio_channel': channel})
            if channel is not None:
                audio_channels.append(channel)
    if sum(x['type'] == 'VideoClipTrack' for x in details) != 1:
        raise ValueError('Expected one cut video track')
    if sorted(audio_channels) != list(range(manifest['audio_channels'])):
        raise ValueError('Native project does not retain all original audio channels')
    digest = hashlib.sha256()
    with Path(manifest['source']).open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(block)
    if digest.hexdigest() != manifest['source_sha256']:
        raise ValueError('Original media changed since detection; inspect before accepting the edit')
    verification_path = work / 'verification.json'
    verification = json.loads(verification_path.read_text())
    verification.update(native_premiere_import_verified=True, native_project=str(project),
                        native_tracks=details, all_native_source_and_timeline_ranges_match=True,
                        source_unchanged_after_edit=True, all_native_media_paths_match_source=True)
    verification_path.write_text(json.dumps(verification, indent=2))
    print(json.dumps(verification, indent=2))


if __name__ == '__main__':
    main()
