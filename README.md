<div align="center">

```text
 ██████╗██╗   ██╗██████╗ ███████╗██████╗     ███████╗██╗  ██╗ ██████╗ ██████╗ ████████╗███████╗
██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗    ██╔════╝██║  ██║██╔═══██╗██╔══██╗╚══██╔══╝██╔════╝
██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝    ███████╗███████║██║   ██║██████╔╝   ██║   ███████╗
██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗    ╚════██║██╔══██║██║   ██║██╔══██╗   ██║   ╚════██║
╚██████╗   ██║   ██████╔╝███████╗██║  ██║    ███████║██║  ██║╚██████╔╝██║  ██║   ██║   ███████║
 ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝    ╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝
                 // BROADCAST AUDIO, LOCAL AI DUBBING & REELS STUDIO v3.3 //
```

<h3>⚡ 100% Local AI Video Editing, Broadcast Voice Mastering, Cloned TTS Dubbing & Viral Shorts Factory ⚡</h3>

<p>
  <img src="https://img.shields.io/badge/PYTHON-3.10%2B-00f3ff?style=for-the-badge&logo=python&logoColor=07090f" alt="Python" />
  <img src="https://img.shields.io/badge/GUI-PyQt6%20HUD-ff007f?style=for-the-badge&logo=qt&logoColor=ffffff" alt="PyQt6" />
  <img src="https://img.shields.io/badge/ENGINE-FFmpeg%20%2B%20Auto--Editor-00ff9c?style=for-the-badge&logo=ffmpeg&logoColor=07090f" alt="FFmpeg" />
  <img src="https://img.shields.io/badge/AI-Ollama%20%2B%20Faster--Whisper-fcee0a?style=for-the-badge&logo=ollama&logoColor=07090f" alt="Ollama" />
  <img src="https://img.shields.io/badge/TTS-F5--TTS%20%7C%20Piper%20%7C%20Edge-9d00ff?style=for-the-badge" alt="TTS" />
  <img src="https://img.shields.io/badge/LANGUAGES-6%20(EN%20ES%20JA%20IT%20AR%20DE)-00f3ff?style=for-the-badge" alt="Multilingual" />
  <img src="https://img.shields.io/badge/LICENSE-MIT-ff007f?style=for-the-badge" alt="License" />
</p>

<p>
  <b>No cloud subscriptions. No API fees. No watermarks.</b><br/>
  Drag &amp; drop raw recordings, dial in radio-grade voice mastering, polish or translate dialogue with local LLMs, re-record with your cloned voice, and batch-export full horizontal, full vertical, and 10–15 viral Shorts in one click.
</p>

</div>

---

## 📸 `[ 01 // INTERFACE & HUD SCREENSHOTS ]`

<img width="1320" height="933" alt="image" src="https://github.com/user-attachments/assets/705e7481-712f-443c-856d-464f0f965297" />


<div align="center">

### Main Studio HUD (Drag & Drop · 5-Band EQ · Live Video/Audio Preview)


<br/><br/>

| 🎛️ Broadcast Audio Rack & VU Meter | 🌐 Multilingual & RTL (Arabic) Mode |
| :---: | :---: |
| <img width="538" height="429" alt="image" src="https://github.com/user-attachments/assets/d860f5e1-6042-459e-9e7e-1e33105714f8" />| <img width="547" height="234" alt="image" src="https://github.com/user-attachments/assets/4e5bae0c-683f-421c-b3c6-39ba76c54d1d" />|

</div>

---

## ⚡ `[ 02 // CORE CAPABILITIES ]`

* **🎛️ Broadcast Audio Mastering Rack:**
  * Auto/manual multi-track microphone selector (auto-picks Track 3 `0:a:2` on multi-track OBS recordings).
  * **5-Band Vertical Equalizer (`±48 dB`)**: `110 Hz` (Lows), `322 Hz` (Low-Mids), `837 Hz` (Mids), `4.8 kHz` (Presence), `10 kHz` (Highs).
  * **Pro FX Switches**: De-Esser (`deesser`), Harmonic Exciter (`aexciter`), Tube Warmth (`asoftclip=tanh`), and Dual-Mono Voice Centering.
  * **Dynamics & Safety**: FFT Denoise (`afftdn`), Noise Gate (`agate`), Voice Compressor, Voice Gain (`-12` to `+36 dB`), and `-0.7 dB` Brickwall Limiter (`alimiter`).
  * **Background Music + Auto-Ducking**: Sidechain compression (`sidechaincompress`) smoothly lowers background music whenever you speak.
* **🎬 Live 15-Second Video & Audio Monitor:**
  * Preview your exact EQ, compression, and music balance at any timestamp inside the embedded player.
  * Real-time **Mean & Peak dB VU Meter** color-coded for Shorts/Reels loudness (`-14 dB` to `-11 dB`).
* **🧠 2-Pass Context-Aware AI Script Polisher & Translator (Ollama):**
  * **Pass 1 (Global Analysis):** Reads the entire transcript to extract the main topic, core message, narrative arc, and unified technical glossary (`video_ALTERED_contexto.json`).
  * **Pass 2 (Coherent Rewriting):** Cleans filler words, fixes Whisper typos, adds natural punctuation, or translates into any of the 6 supported languages while preserving a **±15% word budget** per segment for lip-sync timing.
* **🎙️ Local Voice Cloning & Strict Temporal Lip-Sync:**
  * Auto-discovers local **F5-TTS RAM UNIX Socket daemons** (`/tmp/tts_*.sock`, Fish functions, Bash aliases), **Piper (`.onnx`)**, **Edge-TTS**, and **eSpeak-NG**.
  * Uses word-level Whisper timestamps, edge silence trimming, and smooth `atempo` speed matching (`0.88x–1.38x`) to keep dubbed phrases locked to mouth movement.
* **📦 Multi-Format Automated Export:**
  * Cuts dead air (`>5s`) with `auto-editor` before mixing music so cuts stay razor-sharp.
  * Exports **Full Horizontal (`video_ALTERED.mp4`)** with music baked in, **Full Vertical (`video_ALTERED_VERTICAL.mp4`)** with blurred 1080×1920 framing + burned subtitles, and **10–15 Viral Shorts** sliced directly from the mastered video.
* **💾 Persistent JSON Presets:**
  * Save, load, and manage custom audio profiles in `cyber_shorts_presets.json` with automatic session restore.

---

## 🔄 `[ 03 // PIPELINE ARCHITECTURE ]`

```text
  [ RAW VIDEO(S) + BGM ]
            │
            ▼
  [ 0/7 ] Merge + Voice Mastering (Denoise → Gate → 5-Band EQ → De-Esser → Comp → Limiter)
            │
            ▼
  [ 1/7 ] Silence Removal via auto-editor (clean voice only — zero music interference)
            │
            ▼
  [ 2/7 ] Faster-Whisper Transcription (VAD + Word-Level Lip-Sync Timestamps)
            │
            ▼
  [ 3/7 ] 2-Pass Ollama Script Polisher / Translator ──► video_ALTERED_contexto.json
            │                                        └──► video_ALTERED.srt (synced)
            ▼
  [ 4/7 ] Optional Cloned TTS Re-Recording (F5-TTS RAM Socket / Piper / Edge + Lip-Sync)
            │
            ▼
  [ 5/7 ] Master BGM Mix + Auto-Ducking ───────────────► video_ALTERED.mp4 (Full 16:9)
            │
            ├──► [ 6/7 ] Full Vertical Render ─────────► video_ALTERED_VERTICAL.mp4 (9:16)
            │
            └──► [ 7/7 ] Ollama Viral Clip Extraction ─► 10–15 Vertical Shorts (9:16 + Titles)
```

---

## 🌐 `[ 04 // MULTILINGUAL SUPPORT ]`

Switch the **UI Language** live from the top HUD bar, or mix and match **Source Audio** and **Output Language (AI/TTS)** independently to translate and dub videos across languages.

| Code | Language | Live UI | Layout | FFmpeg Subtitle/Title Font | Built-in TTS Ready |
| :---: | :--- | :---: | :---: | :--- | :---: |
| `en` | **English** | ✅ | LTR | `Liberation Sans` | ✅ |
| `es` | **Español** | ✅ | LTR | `Liberation Sans` | ✅ |
| `ja` | **日本語 (Japanese)** | ✅ | LTR | `Noto Sans CJK JP` | ✅ |
| `it` | **Italiano** | ✅ | LTR | `Liberation Sans` | ✅ |
| `ar` | **العربية (Arabic)** | ✅ | **Auto-RTL** | `Noto Sans Arabic` | ✅ |
| `de` | **Deutsch** | ✅ | LTR | `Liberation Sans` | ✅ |

---

## 🛠️ `[ 05 // INSTALLATION ]`

### 1. System Dependencies

**Arch Linux / CachyOS:**
```bash
sudo pacman -S --needed python python-pip python-pyqt6 qt6-multimedia-ffmpeg ffmpeg noto-fonts noto-fonts-cjk
```

**Debian / Ubuntu / Linux Mint:**
```bash
sudo apt update && sudo apt install -y python3 python3-pip ffmpeg python3-pyqt6 python3-pyqt6.qtmultimedia fonts-noto fonts-noto-cjk
```

### 2. Clone & Install Python Packages

```bash
git clone [https://github.com/julio101290/cyber-shorts-studio.git](https://github.com/julio101290/cyber-shorts-studio.git)
cd cyber-shorts-studio

pip install --user --break-system-packages auto-editor faster-whisper
# Optional (for cloud neural TTS fallback):
pip install --user --break-system-packages edge-tts
```

*(Omit `--break-system-packages` if using a virtual environment or older pip.)*

### 3. Local LLM Setup (Ollama)

Install [Ollama](https://ollama.com/) and pull your preferred model (default is `qwen2.5:14b`):

```bash
ollama pull qwen2.5:14b
```

---

## 🚀 `[ 06 // QUICK START ]`

```bash
python3 cyber_shorts_studio.py
```

1. **Drop your files** into Section `01`: Main Video, optional Second Video to concatenate, and optional Background Music.
2. **Pick your microphone track** (leave on `Auto` for multi-track OBS recordings where your mic is Track 3).
3. **Dial in your voice & music** using the 5-Band EQ, Pro FX toggles, and Dynamics sliders.
4. Set a timestamp where you are actively speaking and click **`⚡ RENDER 15s PREVIEW`**.
   * Aim for a **green VU bar (`-16 dB` to `-10.5 dB` mean)**.
5. *(Optional)* Enable **2-Pass Ollama Dialogue Polishing** and **Cloned TTS Re-Recording**, select your output language, and hit **`▶ GENERATE FULL VIDEOS + SHORTS`**.

---

## 🎙️ `[ 07 // LOCAL VOICE CLONING INTEGRATION ]`

Cyber Shorts Studio automatically scans your Linux system when clicking **`↻`** in Section `06`:

* **F5-TTS / XTTS RAM Socket Daemons:** Detects any script in `~/.local/bin/*.py`, Fish functions (`~/.config/fish/functions/*.fish`), Bash/Zsh aliases, or active `/tmp/tts*.sock` sockets using the JSON UNIX socket protocol (`{"text": "...", "out": "/path/to/out.wav", "lang": "es"}`). If the daemon is stopped, it launches `--daemon` automatically in the background.
* **Piper TTS:** Auto-discovers installed `.onnx` voice models in `~/.local/share/piper`, `~/piper`, and `/usr/share/piper-voices`.
* **Edge-TTS & eSpeak-NG:** Ready out of the box across all 6 languages.

---

## 📁 `[ 08 // OUTPUT ARTIFACTS ]`

| File / Folder | Description |
| :--- | :--- |
| `video_ALTERED.mp4` | Final silence-cut **16:9 Horizontal** master with mastered voice (or TTS) and auto-ducked background music. |
| `video_ALTERED_VERTICAL.mp4` | Full-length **9:16 Vertical (1080×1920)** video with blurred background, centered framing, and burned-in subtitles. |
| `video_ALTERED.srt` | Polished / translated subtitles synced to word-level timestamps. |
| `video_ALTERED_raw.srt` | Backup of the original raw Whisper transcription. |
| `video_ALTERED_contexto.json` | Global topic, narrative arc, and technical glossary extracted during Ollama Pass 1. |
| `cyber_shorts_presets.json` | Saved audio presets and last session state (auto-persisted). |
| `<Output Dir>/*.mp4` | 10 to 15 viral vertical Shorts with bold header titles, subtitles, and embedded metadata. |

---

## 👤 `[ 09 // AUTHOR & COMMUNITY ]`

<div align="center">

Built for Linux creators who want studio-grade automation without cloud lock-in.

[![Website](https://img.shields.io/badge/CESAR_SYSTEMS-cesarsystems.com.mx-00f3ff?style=for-the-badge)](https://cesarsystems.com.mx/)
[![GitHub](https://img.shields.io/badge/GITHUB-julio101290-ff007f?style=for-the-badge&logo=github&logoColor=ffffff)](https://github.com/julio101290/)
[![YouTube](https://img.shields.io/badge/YOUTUBE-@CesarSystem-ff0033?style=for-the-badge&logo=youtube&logoColor=ffffff)](https://www.youtube.com/@CesarSystem)
[![Telegram](https://img.shields.io/badge/TELEGRAM-CesarSystems-0088cc?style=for-the-badge&logo=telegram&logoColor=ffffff)](https://t.me/CesarSystems)
[![Patreon](https://img.shields.io/badge/PATREON-Support-fcee0a?style=for-the-badge&logo=patreon&logoColor=07090f)](https://www.patreon.com/c/u74078772)

<sub>Released under the <b>MIT License</b>. Feel free to fork, hack, and broadcast.</sub>

</div>
