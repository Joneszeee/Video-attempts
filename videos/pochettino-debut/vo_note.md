Voiceover: the user records on ElevenLabs from vo_elevenlabs.md (one file); align with engine/align_vo.py against the Kokoro read out/vo.wav.
Build: `python3 build.py videos/pochettino-debut/spec.json --vo videos/pochettino-debut/out/voice.mp3 --out videos/pochettino-debut/out/pochettino-debut_final.mp4`
(copy the upload to out/voice.mp3 first; out/ is gitignored, so re-run tts.py + align_vo.py if the reference or alignment file is missing).
