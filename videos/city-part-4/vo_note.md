Voiceover: the user records on ElevenLabs from vo_elevenlabs.md (one file); align with engine/align_vo.py against the Kokoro read out/vo.wav.
Build: `python3 build.py videos/city-part-4/spec.json --vo videos/city-part-4/out/voice.mp3 --out videos/city-part-4/out/city-part-4_final.mp4`
(copy the upload to out/voice.mp3 first; out/ is gitignored, so re-run tts.py + align_vo.py if the reference or alignment file is missing).
After the real voice is in, run `python3 engine/check.py videos/city-part-4 --video <final mp4>` again: the cues move with the voice, so shots under 2 s can appear.
