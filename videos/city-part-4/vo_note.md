Voiceover: the user records on ElevenLabs from vo_elevenlabs.md (one file); align with engine/align_vo.py against the Kokoro read out/vo.wav.
Build: `python3 build.py videos/city-part-4/spec.json --vo videos/city-part-4/out/voice.mp3 --out videos/city-part-4/out/city-part-4_final.mp4`
(copy the upload to out/voice.mp3 first; out/ is gitignored, so re-run tts.py + align_vo.py if the reference or alignment file is missing).
After the real voice is in, run `python3 engine/check.py videos/city-part-4 --video <final mp4>` again: the cues move with the voice, so shots under 2 s can appear.

Done 23 Nov 2026: the user's upload (P5.mp3) is out/voice.mp3, aligned (line starts at 0.0, 3.50, 9.72, 13.23, 18.00, 23.78, 27.31, 32.34, 37.22, 41.21, 46.82, 53.07, 57.60, 61.36 s), the last shot's cut nudged to lag 0.32 for the real timing; final = out/city-part-4_final.mp4.
