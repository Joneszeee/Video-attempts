Voiceover: the user records on ElevenLabs from vo_elevenlabs.md (one file); align with engine/align_vo.py against the Kokoro read out/vo.wav.
Build: `python3 build.py videos/city-part-5/spec.json --vo videos/city-part-5/out/voice.mp3 --out videos/city-part-5/out/city-part-5_final.mp4`
(copy the upload to out/voice.mp3 first; out/ is gitignored, so re-run tts.py + align_vo.py if the reference or alignment file is missing).
Kokoro reference: `KOKORO_DIR=<folder with kokoro-v1.0.onnx and voices-v1.0.bin> python3 engine/tts.py videos/city-part-5/vo.txt videos/city-part-5/out/vo.wav --gap 0.45` (13 lines, 70.4 s).
After the real voice is in, run `python3 engine/check.py videos/city-part-5 --video <final mp4>` again: the cues move with the voice, so shots under 2 s can appear
(the last two shots in beat 12 and the second shot of beat 10 are the short ones to watch).
