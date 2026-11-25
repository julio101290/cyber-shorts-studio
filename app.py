#!/usr/bin/env python3
import array
import importlib.util
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
import wave
from pathlib import Path

# Reduce advertencias inofensivas de Qt6 en Wayland y del backend multimedia
os.environ.setdefault("QT_LOGGING_RULES", "qt.qpa.wayland=false;qt.multimedia.ffmpeg=false")

from PyQt6.QtCore import Qt, QThread, QUrl, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# --- CONFIGURACIÓN POR DEFECTO ---
DEFAULT_OUT_DIR = "/home/julioc/Automatizaciones/shorts/global/tutoriales"
DEFAULT_OLLAMA_MODEL = "qwen2.5:14b"
OLLAMA_URL = "http://localhost:11434/api/generate"
PRESETS_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "cyber_shorts_presets.json"
)

# =====================================================================
# TRADUCCIONES MULTILENGUAJE (ES, EN, JA, IT, AR, DE)
# =====================================================================

LANG_META = {
    "es": {"name": "Español", "prompt_name": "Español Latino", "font": "Liberation Sans", "sample": "Hola, esta es una prueba de voz clonada con dicción clara para tus videos."},
    "en": {"name": "English", "prompt_name": "English", "font": "Liberation Sans", "sample": "Hello, this is a voice test with clear broadcast diction for your videos."},
    "ja": {"name": "日本語", "prompt_name": "Japanese (日本語)", "font": "Noto Sans CJK JP", "sample": "こんにちは、動画やショート用のクリアな音声テストです。"},
    "it": {"name": "Italiano", "prompt_name": "Italian (Italiano)", "font": "Liberation Sans", "sample": "Ciao, questa è una prova vocale con dizione chiara per i tuoi video."},
    "ar": {"name": "العربية", "prompt_name": "Arabic (العربية)", "font": "Noto Sans Arabic", "sample": "مرحباً، هذا اختبار صوتي بنطق واضح واحترافي لمقاطع الفيديو الخاصة بك."},
    "de": {"name": "Deutsch", "prompt_name": "German (Deutsch)", "font": "Liberation Sans", "sample": "Hallo, dies ist ein Sprachtest mit klarer Aussprache für deine Videos."},
}

TRANSLATIONS = {
    "es": {
        "win_title": "CYBER_SHORTS // ESTUDIO BROADCAST DE AUDIO, TTS Y SINCRONÍA v3.3",
        "header_title": "⚡ CYBER_SHORTS // ESTUDIO AUDIO, TTS & REELS v3.3",
        "ui_lang_lbl": "Idioma UI:",
        "status_standby": "ESTADO: EN ESPERA",
        "status_preview_run": "ESTADO: RENDERIZANDO PREVIEW...",
        "status_preview_ok": "ESTADO: PREVIEW LISTO",
        "status_preview_err": "ESTADO: ERROR EN PREVIEW",
        "status_tts_run": "ESTADO: PROBANDO VOZ TTS...",
        "status_tts_ok": "ESTADO: PRUEBA TTS LISTA",
        "status_tts_err": "ESTADO: ERROR EN TTS",
        "status_pipe_run": "ESTADO: PROCESANDO PIPELINE...",
        "status_pipe_ok": "ESTADO: COMPLETADO",
        "status_pipe_err": "ESTADO: ERROR",
        "sec_01": "[ 01 // ARCHIVOS DE ENTRADA (DRAG & DROP) ]",
        "drop_v1": "VIDEO PRINCIPAL (.mp4 / .mkv)",
        "drop_v2": "VIDEO EXTRA OPCIONAL (.mp4 / .mkv)",
        "drop_music": "MÚSICA DE FONDO (.mp3 / .wav)",
        "drop_hint": "[Arrastra o clic]",
        "tip_clear_music": "Quitar música de fondo",
        "mic_track": "Pista Micrófono:",
        "track_auto": "Auto (Pista 3 si existen ≥3)",
        "track_n": "Pista {n} (0:a:{i})",
        "sec_02": "[ 02 // PRESETS GUARDADOS (JSON) ]",
        "btn_load": "CARGAR",
        "btn_save": "GUARDAR",
        "tip_del_preset": "Eliminar preset seleccionado",
        "dlg_save_title": "Guardar Preset",
        "dlg_save_prompt": "Nombre del preset:",
        "sec_03": "[ 03 // ECUALIZADOR (BAJOS · MEDIOS · ALTOS) ]",
        "eq_low": "BAJOS", "eq_lowmid": "MED-B", "eq_mid": "MEDIOS", "eq_pres": "PRES.", "eq_high": "ALTOS",
        "sec_04": "[ 04 // RACK DE EFECTOS PRO ]",
        "fx_deesser": "De-Esser (suaviza 'S')",
        "fx_exciter": "Excitador (aire estudio)",
        "fx_warmth": "Calidez Bulbos (Tube)",
        "fx_dual_mono": "Centrar Voz (Dual-Mono)",
        "sec_05": "[ 05 // DINÁMICA, VOLUMEN & MÚSICA ]",
        "lbl_voice_gain": "Ganancia Voz (dB)",
        "lbl_comp_ratio": "Compresor (Ratio)",
        "lbl_gate": "Puerta de Ruido",
        "lbl_music_db": "Volumen Música",
        "chk_ducking": "AUTO-DUCKING (baja música cuando hablas)",
        "sec_06": "[ 06 // GUIÓN IA (2 PASADAS), REGRABAR VOZ & SINCRONÍA ]",
        "lbl_src_lang": "Idioma Audio (Whisper):",
        "lbl_dst_lang": "Idioma Salida (IA/TTS):",
        "lang_auto": "Auto-detectar",
        "chk_polish": "Pulir / traducir diálogos con Ollama (contexto global + tiempos)",
        "chk_use_tts": "Regrabar toda la voz con TTS clonado / local",
        "btn_tts_test": "🔊 PROBAR",
        "tip_tts_scan": "Reescanear voces clonadas / TTS instaladas",
        "no_tts": "(No se detectaron motores TTS)",
        "chk_lipsync": "Sincronía labial estricta (ajusta ritmo de cada frase a tu boca)",
        "chk_tts_rack": "Aplicar Rack EQ/Comp a voz TTS (desmarcado = pulido limpio)",
        "sec_07": "[ 07 // SALIDA, FORMATOS & IA ]",
        "chk_full_vert": "Generar también video completo en VERTICAL (video_ALTERED_VERTICAL.mp4)",
        "btn_dir": "DIR",
        "dlg_outdir": "Seleccionar carpeta de salida",
        "lbl_ollama": "Ollama:",
        "chk_force": "Reprocesar caché",
        "btn_run": "▶ GENERAR VIDEOS COMPLETOS + SHORTS (PIPELINE IA)",
        "sec_08": "[ 08 // MONITOR DE VISTA PREVIA (VIDEO + AUDIO) ]",
        "lbl_prev_start": "Inicio preview (seg):",
        "btn_preview": "⚡ GENERAR PREVIEW 15s",
        "btn_play": "⏯ PLAY/PAUSE",
        "meter_idle": "MEDIDOR AUDIO: Sin medir | Objetivo Shorts: -14 dB a -11 dB",
        "vu_idle": "NIVEL MEDIO: -- dB",
        "vu_fmt": "MEDIO: {mean:.1f} dB  |  PICO: {max:.1f} dB",
        "lvl_ok": "ESTADO AUDIO: ÓPTIMO PARA SHORTS",
        "lvl_low": "ESTADO AUDIO: UN POCO BAJO (sube Ganancia Voz)",
        "lvl_high": "ESTADO AUDIO: MUY ALTO (baja Ganancia Voz)",
        "sec_09": "[ 09 // CONSOLA DE SISTEMA ]",
        "err_no_video": "[!] Arrastra primero el video principal.",
        "err_no_tts": "[!] No hay ninguna voz TTS disponible para probar.",
        "files_filter": "Archivos",
    },
    "en": {
        "win_title": "CYBER_SHORTS // BROADCAST AUDIO, TTS & LIP-SYNC STUDIO v3.3",
        "header_title": "⚡ CYBER_SHORTS // AUDIO, TTS & REELS STUDIO v3.3",
        "ui_lang_lbl": "UI Language:",
        "status_standby": "STATUS: STANDBY",
        "status_preview_run": "STATUS: RENDERING PREVIEW...",
        "status_preview_ok": "STATUS: PREVIEW READY",
        "status_preview_err": "STATUS: PREVIEW ERROR",
        "status_tts_run": "STATUS: TESTING TTS VOICE...",
        "status_tts_ok": "STATUS: TTS TEST READY",
        "status_tts_err": "STATUS: TTS ERROR",
        "status_pipe_run": "STATUS: PROCESSING PIPELINE...",
        "status_pipe_ok": "STATUS: COMPLETED",
        "status_pipe_err": "STATUS: ERROR",
        "sec_01": "[ 01 // INPUT FILES (DRAG & DROP) ]",
        "drop_v1": "MAIN VIDEO (.mp4 / .mkv)",
        "drop_v2": "OPTIONAL EXTRA VIDEO (.mp4 / .mkv)",
        "drop_music": "BACKGROUND MUSIC (.mp3 / .wav)",
        "drop_hint": "[Drop or click]",
        "tip_clear_music": "Remove background music",
        "mic_track": "Microphone Track:",
        "track_auto": "Auto (Track 3 if ≥3 exist)",
        "track_n": "Track {n} (0:a:{i})",
        "sec_02": "[ 02 // SAVED PRESETS (JSON) ]",
        "btn_load": "LOAD",
        "btn_save": "SAVE",
        "tip_del_preset": "Delete selected preset",
        "dlg_save_title": "Save Preset",
        "dlg_save_prompt": "Preset name:",
        "sec_03": "[ 03 // EQUALIZER (LOWS · MIDS · HIGHS) ]",
        "eq_low": "LOWS", "eq_lowmid": "LOW-M", "eq_mid": "MIDS", "eq_pres": "PRES.", "eq_high": "HIGHS",
        "sec_04": "[ 04 // PRO EFFECTS RACK ]",
        "fx_deesser": "De-Esser (tames 'S')",
        "fx_exciter": "Exciter (studio air)",
        "fx_warmth": "Tube Warmth (softclip)",
        "fx_dual_mono": "Center Voice (Dual-Mono)",
        "sec_05": "[ 05 // DYNAMICS, VOLUME & MUSIC ]",
        "lbl_voice_gain": "Voice Gain (dB)",
        "lbl_comp_ratio": "Compressor (Ratio)",
        "lbl_gate": "Noise Gate",
        "lbl_music_db": "Music Volume",
        "chk_ducking": "AUTO-DUCKING (lowers music while speaking)",
        "sec_06": "[ 06 // AI SCRIPT (2-PASS), VOICE DUB & LIP-SYNC ]",
        "lbl_src_lang": "Source Audio (Whisper):",
        "lbl_dst_lang": "Output Lang (AI/TTS):",
        "lang_auto": "Auto-detect",
        "chk_polish": "Polish / translate dialogues with Ollama (global context + timing)",
        "chk_use_tts": "Re-record full voice using cloned / local TTS",
        "btn_tts_test": "🔊 TEST",
        "tip_tts_scan": "Rescan installed cloned / TTS voices",
        "no_tts": "(No TTS engines detected)",
        "chk_lipsync": "Strict lip-sync (fits each phrase timing to mouth movement)",
        "chk_tts_rack": "Apply EQ/Comp Rack to TTS voice (unchecked = clean polish)",
        "sec_07": "[ 07 // OUTPUT, FORMATS & AI ]",
        "chk_full_vert": "Also render full VERTICAL video (video_ALTERED_VERTICAL.mp4)",
        "btn_dir": "DIR",
        "dlg_outdir": "Select output folder",
        "lbl_ollama": "Ollama:",
        "chk_force": "Reprocess cache",
        "btn_run": "▶ GENERATE FULL VIDEOS + SHORTS (AI PIPELINE)",
        "sec_08": "[ 08 // PREVIEW MONITOR (VIDEO + AUDIO) ]",
        "lbl_prev_start": "Preview start (sec):",
        "btn_preview": "⚡ RENDER 15s PREVIEW",
        "btn_play": "⏯ PLAY/PAUSE",
        "meter_idle": "AUDIO METER: Not measured | Shorts target: -14 dB to -11 dB",
        "vu_idle": "MEAN LEVEL: -- dB",
        "vu_fmt": "MEAN: {mean:.1f} dB  |  PEAK: {max:.1f} dB",
        "lvl_ok": "AUDIO STATUS: OPTIMAL FOR SHORTS",
        "lvl_low": "AUDIO STATUS: A BIT LOW (raise Voice Gain)",
        "lvl_high": "AUDIO STATUS: TOO LOUD (lower Voice Gain)",
        "sec_09": "[ 09 // SYSTEM CONSOLE ]",
        "err_no_video": "[!] Drop the main video first.",
        "err_no_tts": "[!] No TTS voice available to test.",
        "files_filter": "Files",
    },
    "ja": {
        "win_title": "CYBER_SHORTS // ブロードキャスト音声・TTS・リップシンクスタジオ v3.3",
        "header_title": "⚡ CYBER_SHORTS // 音声・TTS＆ショート制作スタジオ v3.3",
        "ui_lang_lbl": "表示言語:",
        "status_standby": "状態: 待機中",
        "status_preview_run": "状態: プレビュー生成中...",
        "status_preview_ok": "状態: プレビュー準備完了",
        "status_preview_err": "状態: プレビューエラー",
        "status_tts_run": "状態: TTS音声テスト中...",
        "status_tts_ok": "状態: TTSテスト完了",
        "status_tts_err": "状態: TTSエラー",
        "status_pipe_run": "状態: パイプライン処理中...",
        "status_pipe_ok": "状態: 完了",
        "status_pipe_err": "状態: エラー",
        "sec_01": "[ 01 // 入力ファイル (ドラッグ＆ドロップ) ]",
        "drop_v1": "メイン動画 (.mp4 / .mkv)",
        "drop_v2": "追加動画・任意 (.mp4 / .mkv)",
        "drop_music": "BGM音楽・任意 (.mp3 / .wav)",
        "drop_hint": "[ドロップまたはクリック]",
        "tip_clear_music": "BGMを削除",
        "mic_track": "マイクトラック:",
        "track_auto": "自動 (3トラック以上なら3番目)",
        "track_n": "トラック {n} (0:a:{i})",
        "sec_02": "[ 02 // 保存プリセット (JSON) ]",
        "btn_load": "読込",
        "btn_save": "保存",
        "tip_del_preset": "選択中のプリセットを削除",
        "dlg_save_title": "プリセット保存",
        "dlg_save_prompt": "プリセット名:",
        "sec_03": "[ 03 // イコライザー (低音 · 中音 · 高音) ]",
        "eq_low": "低音", "eq_lowmid": "中低", "eq_mid": "中音", "eq_pres": "明瞭", "eq_high": "高音",
        "sec_04": "[ 04 // プロ・エフェクトラック ]",
        "fx_deesser": "ディエッサー (歯擦音軽減)",
        "fx_exciter": "エキサイター (空気感)",
        "fx_warmth": "真空管ウォーム (Tube)",
        "fx_dual_mono": "音声センター化 (Dual-Mono)",
        "sec_05": "[ 05 // ダイナミクス・音量＆BGM ]",
        "lbl_voice_gain": "声のゲイン (dB)",
        "lbl_comp_ratio": "コンプレッサー比率",
        "lbl_gate": "ノイズゲート",
        "lbl_music_db": "BGM音量",
        "chk_ducking": "オートダッキング (発話時にBGMを自動減衰)",
        "sec_06": "[ 06 // AI台本整形 (2パス)・TTS吹替＆リップシンク ]",
        "lbl_src_lang": "入力音声言語 (Whisper):",
        "lbl_dst_lang": "出力言語 (AI/TTS):",
        "lang_auto": "自動検出",
        "chk_polish": "Ollamaでセリフを整形・翻訳 (全体文脈＋尺維持)",
        "chk_use_tts": "クローン／ローカルTTSで全音声を再収録",
        "btn_tts_test": "🔊 テスト",
        "tip_tts_scan": "インストール済みTTS音声を再スキャン",
        "no_tts": "(TTSエンジンが見つかりません)",
        "chk_lipsync": "厳密リップシンク (口の動きに合わせて速度微調整)",
        "chk_tts_rack": "TTS音声にもEQ/コンプを適用 (未選択=クリーン処理)",
        "sec_07": "[ 07 // 出力・フォーマット＆AI ]",
        "chk_full_vert": "縦型フル動画も生成 (video_ALTERED_VERTICAL.mp4)",
        "btn_dir": "選択",
        "dlg_outdir": "出力フォルダを選択",
        "lbl_ollama": "Ollama:",
        "chk_force": "キャッシュ再処理",
        "btn_run": "▶ フル動画＋ショート一括生成 (AIパイプライン)",
        "sec_08": "[ 08 // プレビューモニター (映像＋音声) ]",
        "lbl_prev_start": "開始位置 (秒):",
        "btn_preview": "⚡ 15秒プレビュー生成",
        "btn_play": "⏯ 再生/一時停止",
        "meter_idle": "音量メーター: 未計測 | ショート推奨: -14 dB 〜 -11 dB",
        "vu_idle": "平均レベル: -- dB",
        "vu_fmt": "平均: {mean:.1f} dB  |  ピーク: {max:.1f} dB",
        "lvl_ok": "音声状態: ショートに最適",
        "lvl_low": "音声状態: やや小さめ (声のゲインを上げてください)",
        "lvl_high": "音声状態: 大きすぎます (声のゲインを下げてください)",
        "sec_09": "[ 09 // システムコンソール ]",
        "err_no_video": "[!] 先にメイン動画をドロップしてください。",
        "err_no_tts": "[!] テスト可能なTTS音声がありません。",
        "files_filter": "ファイル",
    },
    "it": {
        "win_title": "CYBER_SHORTS // STUDIO AUDIO BROADCAST, TTS & LIP-SYNC v3.3",
        "header_title": "⚡ CYBER_SHORTS // STUDIO AUDIO, TTS & REELS v3.3",
        "ui_lang_lbl": "Lingua UI:",
        "status_standby": "STATO: IN ATTESA",
        "status_preview_run": "STATO: RENDERING ANTEPRIMA...",
        "status_preview_ok": "STATO: ANTEPRIMA PRONTA",
        "status_preview_err": "STATO: ERRORE ANTEPRIMA",
        "status_tts_run": "STATO: TEST VOCE TTS...",
        "status_tts_ok": "STATO: TEST TTS PRONTO",
        "status_tts_err": "STATO: ERRORE TTS",
        "status_pipe_run": "STATO: ELABORAZIONE PIPELINE...",
        "status_pipe_ok": "STATO: COMPLETATO",
        "status_pipe_err": "STATO: ERRORE",
        "sec_01": "[ 01 // FILE DI INPUT (DRAG & DROP) ]",
        "drop_v1": "VIDEO PRINCIPALE (.mp4 / .mkv)",
        "drop_v2": "VIDEO EXTRA OPZIONALE (.mp4 / .mkv)",
        "drop_music": "MUSICA DI SOTTOFONDO (.mp3 / .wav)",
        "drop_hint": "[Trascina o clicca]",
        "tip_clear_music": "Rimuovi musica di sottofondo",
        "mic_track": "Traccia Microfono:",
        "track_auto": "Auto (Traccia 3 se ≥3 presenti)",
        "track_n": "Traccia {n} (0:a:{i})",
        "sec_02": "[ 02 // PRESET SALVATI (JSON) ]",
        "btn_load": "CARICA",
        "btn_save": "SALVA",
        "tip_del_preset": "Elimina preset selezionato",
        "dlg_save_title": "Salva Preset",
        "dlg_save_prompt": "Nome del preset:",
        "sec_03": "[ 03 // EQUALIZZATORE (BASSI · MEDI · ALTI) ]",
        "eq_low": "BASSI", "eq_lowmid": "MED-B", "eq_mid": "MEDI", "eq_pres": "PRES.", "eq_high": "ALTI",
        "sec_04": "[ 04 // RACK EFFETTI PRO ]",
        "fx_deesser": "De-Esser (attenua le 'S')",
        "fx_exciter": "Exciter (aria da studio)",
        "fx_warmth": "Calore Valvolare (Tube)",
        "fx_dual_mono": "Centra Voce (Dual-Mono)",
        "sec_05": "[ 05 // DINAMICA, VOLUME & MUSICA ]",
        "lbl_voice_gain": "Guadagno Voce (dB)",
        "lbl_comp_ratio": "Compressore (Ratio)",
        "lbl_gate": "Noise Gate",
        "lbl_music_db": "Volume Musica",
        "chk_ducking": "AUTO-DUCKING (abbassa la musica mentre parli)",
        "sec_06": "[ 06 // COPIONE IA (2 PASSI), DOPPIAGGIO TTS & LIP-SYNC ]",
        "lbl_src_lang": "Lingua Audio (Whisper):",
        "lbl_dst_lang": "Lingua Output (IA/TTS):",
        "lang_auto": "Rilevamento auto",
        "chk_polish": "Migliora / traduci dialoghi con Ollama (contesto globale + tempi)",
        "chk_use_tts": "Riregistra tutta la voce con TTS clonato / locale",
        "btn_tts_test": "🔊 PROVA",
        "tip_tts_scan": "Scansiona nuovamente le voci TTS installate",
        "no_tts": "(Nessun motore TTS rilevato)",
        "chk_lipsync": "Lip-sync rigoroso (adatta il ritmo al movimento labiale)",
        "chk_tts_rack": "Applica Rack EQ/Comp alla voce TTS (disattivo = pulizia neutra)",
        "sec_07": "[ 07 // OUTPUT, FORMATI & IA ]",
        "chk_full_vert": "Genera anche video completo VERTICALE (video_ALTERED_VERTICAL.mp4)",
        "btn_dir": "DIR",
        "dlg_outdir": "Seleziona cartella di output",
        "lbl_ollama": "Ollama:",
        "chk_force": "Rielabora cache",
        "btn_run": "▶ GENERA VIDEO COMPLETI + SHORTS (PIPELINE IA)",
        "sec_08": "[ 08 // MONITOR ANTEPRIMA (VIDEO + AUDIO) ]",
        "lbl_prev_start": "Inizio anteprima (sec):",
        "btn_preview": "⚡ ANTEPRIMA 15s",
        "btn_play": "⏯ PLAY/PAUSA",
        "meter_idle": "MISURATORE AUDIO: Non misurato | Target Shorts: da -14 a -11 dB",
        "vu_idle": "LIVELLO MEDIO: -- dB",
        "vu_fmt": "MEDIO: {mean:.1f} dB  |  PICCO: {max:.1f} dB",
        "lvl_ok": "STATO AUDIO: OTTIMALE PER SHORTS",
        "lvl_low": "STATO AUDIO: UN PO' BASSO (alza Guadagno Voce)",
        "lvl_high": "STATO AUDIO: TROPPO ALTO (abbassa Guadagno Voce)",
        "sec_09": "[ 09 // CONSOLE DI SISTEMA ]",
        "err_no_video": "[!] Trascina prima il video principale.",
        "err_no_tts": "[!] Nessuna voce TTS disponibile per il test.",
        "files_filter": "File",
    },
    "ar": {
        "win_title": "CYBER_SHORTS // استوديو الصوت الاحترافي والدبلجة والمزامنة v3.3",
        "header_title": "⚡ CYBER_SHORTS // استوديو الصوت والـ TTS والريلز v3.3",
        "ui_lang_lbl": "لغة الواجهة:",
        "status_standby": "الحالة: جاهز",
        "status_preview_run": "الحالة: جارٍ إنشاء المعاينة...",
        "status_preview_ok": "الحالة: المعاينة جاهزة",
        "status_preview_err": "الحالة: خطأ في المعاينة",
        "status_tts_run": "الحالة: جارٍ اختبار الصوت...",
        "status_tts_ok": "الحالة: اختبار الصوت جاهز",
        "status_tts_err": "الحالة: خطأ في TTS",
        "status_pipe_run": "الحالة: جارٍ المعالجة الكاملة...",
        "status_pipe_ok": "الحالة: اكتمل بنجاح",
        "status_pipe_err": "الحالة: حدث خطأ",
        "sec_01": "[ 01 // ملفات الإدخال (سحب وإفلات) ]",
        "drop_v1": "الفيديو الرئيسي (.mp4 / .mkv)",
        "drop_v2": "فيديو إضافي اختياري (.mp4 / .mkv)",
        "drop_music": "موسيقى خلفية اختيارية (.mp3 / .wav)",
        "drop_hint": "[اسحب هنا أو انقر]",
        "tip_clear_music": "إزالة الموسيقى الخلفية",
        "mic_track": "مسار الميكروفون:",
        "track_auto": "تلقائي (المسار 3 إذا وجد ≥3)",
        "track_n": "المسار {n} (0:a:{i})",
        "sec_02": "[ 02 // الإعدادات المحفوظة (JSON) ]",
        "btn_load": "تحميل",
        "btn_save": "حفظ",
        "tip_del_preset": "حذف الإعداد المحدد",
        "dlg_save_title": "حفظ إعداد مسبق",
        "dlg_save_prompt": "اسم الإعداد:",
        "sec_03": "[ 03 // معادل الصوت (جهير · متوسط · حاد) ]",
        "eq_low": "جهير", "eq_lowmid": "متوسط-", "eq_mid": "متوسط", "eq_pres": "وضوح", "eq_high": "حاد",
        "sec_04": "[ 04 // مؤثرات الاستوديو الاحترافية ]",
        "fx_deesser": "De-Esser (تخفيف حرف السّين)",
        "fx_exciter": "Exciter (لمعان استوديو)",
        "fx_warmth": "دفء أنبوبي (Tube)",
        "fx_dual_mono": "توسيط الصوت (Dual-Mono)",
        "sec_05": "[ 05 // الديناميكيات ومستوى الصوت والموسيقى ]",
        "lbl_voice_gain": "تضخيم الصوت (dB)",
        "lbl_comp_ratio": "الضاغط (النسبة)",
        "lbl_gate": "بوابة الضوضاء",
        "lbl_music_db": "مستوى الموسيقى",
        "chk_ducking": "خفض تلقائي للموسيقى أثناء الكلام (Auto-Ducking)",
        "sec_06": "[ 06 // تحسين النص (مرحلتان)، الدبلجة ومزامنة الشفاه ]",
        "lbl_src_lang": "لغة الفيديو (Whisper):",
        "lbl_dst_lang": "لغة الإخراج (AI/TTS):",
        "lang_auto": "كشف تلقائي",
        "chk_polish": "تحسين / ترجمة الحوار عبر Ollama (سياق كامل + توقيت)",
        "chk_use_tts": "إعادة تسجيل الصوت بالكامل باستخدام TTS محلي / مستنسخ",
        "btn_tts_test": "🔊 اختبار",
        "tip_tts_scan": "إعادة فحص الأصوات المثبتة",
        "no_tts": "(لم يتم العثور على محركات TTS)",
        "chk_lipsync": "مزامنة شفاه دقيقة (ضبط سرعة كل جملة مع حركة الفم)",
        "chk_tts_rack": "تطبيق معادل الصوت على TTS (غير محدد = معالجة نظيفة)",
        "sec_07": "[ 07 // الإخراج والصيغ والذكاء الاصطناعي ]",
        "chk_full_vert": "إنشاء فيديو عمودي كامل أيضاً (video_ALTERED_VERTICAL.mp4)",
        "btn_dir": "مجلد",
        "dlg_outdir": "اختر مجلد الإخراج",
        "lbl_ollama": "Ollama:",
        "chk_force": "إعادة معالجة الكاش",
        "btn_run": "▶ إنشاء الفيديوهات الكاملة + المقاطع القصيرة (AI)",
        "sec_08": "[ 08 // شاشة المعاينة (فيديو + صوت) ]",
        "lbl_prev_start": "بداية المعاينة (ثانية):",
        "btn_preview": "⚡ معاينة 15 ثانية",
        "btn_play": "⏯ تشغيل/إيقاف",
        "meter_idle": "مقياس الصوت: غير مقاس | المستهدف للقصيرة: -14 إلى -11 dB",
        "vu_idle": "المستوى المتوسط: -- dB",
        "vu_fmt": "المتوسط: {mean:.1f} dB  |  الذروة: {max:.1f} dB",
        "lvl_ok": "حالة الصوت: مثالي للمقاطع القصيرة",
        "lvl_low": "حالة الصوت: منخفض قليلاً (ارفع تضخيم الصوت)",
        "lvl_high": "حالة الصوت: مرتفع جداً (اخفض تضخيم الصوت)",
        "sec_09": "[ 09 // وحدة تحكم النظام ]",
        "err_no_video": "[!] اسحب الفيديو الرئيسي أولاً.",
        "err_no_tts": "[!] لا يوجد صوت TTS متاح للاختبار.",
        "files_filter": "ملفات",
    },
    "de": {
        "win_title": "CYBER_SHORTS // BROADCAST AUDIO-, TTS- & LIP-SYNC-STUDIO v3.3",
        "header_title": "⚡ CYBER_SHORTS // AUDIO-, TTS- & REELS-STUDIO v3.3",
        "ui_lang_lbl": "UI-Sprache:",
        "status_standby": "STATUS: BEREIT",
        "status_preview_run": "STATUS: VORSCHAU WIRD GERENDERT...",
        "status_preview_ok": "STATUS: VORSCHAU BEREIT",
        "status_preview_err": "STATUS: VORSCHAU-FEHLER",
        "status_tts_run": "STATUS: TTS-STIMME WIRD GETESTET...",
        "status_tts_ok": "STATUS: TTS-TEST BEREIT",
        "status_tts_err": "STATUS: TTS-FEHLER",
        "status_pipe_run": "STATUS: PIPELINE LÄUFT...",
        "status_pipe_ok": "STATUS: ABGESCHLOSSEN",
        "status_pipe_err": "STATUS: FEHLER",
        "sec_01": "[ 01 // EINGABEDATEIEN (DRAG & DROP) ]",
        "drop_v1": "HAUPTVIDEO (.mp4 / .mkv)",
        "drop_v2": "ZUSATZVIDEO OPTIONAL (.mp4 / .mkv)",
        "drop_music": "HINTERGRUNDMUSIK (.mp3 / .wav)",
        "drop_hint": "[Ziehen oder klicken]",
        "tip_clear_music": "Hintergrundmusik entfernen",
        "mic_track": "Mikrofonspur:",
        "track_auto": "Auto (Spur 3 bei ≥3 Spuren)",
        "track_n": "Spur {n} (0:a:{i})",
        "sec_02": "[ 02 // GESPEICHERTE PRESETS (JSON) ]",
        "btn_load": "LADEN",
        "btn_save": "SPEICHERN",
        "tip_del_preset": "Ausgewähltes Preset löschen",
        "dlg_save_title": "Preset speichern",
        "dlg_save_prompt": "Preset-Name:",
        "sec_03": "[ 03 // EQUALIZER (BÄSSE · MITTEN · HÖHEN) ]",
        "eq_low": "BASS", "eq_lowmid": "T-MIT", "eq_mid": "MITTE", "eq_pres": "PRÄS.", "eq_high": "HÖHEN",
        "sec_04": "[ 04 // PRO-EFFEKTRACK ]",
        "fx_deesser": "De-Esser (mildert Zischlaute)",
        "fx_exciter": "Exciter (Studio-Brillanz)",
        "fx_warmth": "Röhrenwärme (Tube)",
        "fx_dual_mono": "Stimme zentrieren (Dual-Mono)",
        "sec_05": "[ 05 // DYNAMIK, LAUTSTÄRKE & MUSIK ]",
        "lbl_voice_gain": "Stimm-Gain (dB)",
        "lbl_comp_ratio": "Kompressor (Ratio)",
        "lbl_gate": "Noise Gate",
        "lbl_music_db": "Musiklautstärke",
        "chk_ducking": "AUTO-DUCKING (senkt Musik beim Sprechen)",
        "sec_06": "[ 06 // KI-SKRIPT (2-PASS), TTS-SYNCHRO & LIP-SYNC ]",
        "lbl_src_lang": "Quell-Audio (Whisper):",
        "lbl_dst_lang": "Zielsprache (KI/TTS):",
        "lang_auto": "Automatisch",
        "chk_polish": "Dialoge mit Ollama glätten / übersetzen (Kontext + Timing)",
        "chk_use_tts": "Gesamte Stimme mit lokalem / geklontem TTS neu einsprechen",
        "btn_tts_test": "🔊 TEST",
        "tip_tts_scan": "Installierte TTS-Stimmen neu scannen",
        "no_tts": "(Keine TTS-Engines gefunden)",
        "chk_lipsync": "Strenges Lip-Sync (passt Sprechtempo an Mundbewegung an)",
        "chk_tts_rack": "EQ/Kompressor-Rack auf TTS anwenden (aus = neutraler Schliff)",
        "sec_07": "[ 07 // AUSGABE, FORMATE & KI ]",
        "chk_full_vert": "Auch komplettes VERTIKAL-Video erstellen (video_ALTERED_VERTICAL.mp4)",
        "btn_dir": "ORDNER",
        "dlg_outdir": "Ausgabeordner wählen",
        "lbl_ollama": "Ollama:",
        "chk_force": "Cache neu erstellen",
        "btn_run": "▶ KOMPLETTVIDEOS + SHORTS GENERIEREN (KI-PIPELINE)",
        "sec_08": "[ 08 // VORSCHAU-MONITOR (VIDEO + AUDIO) ]",
        "lbl_prev_start": "Vorschau-Start (Sek.):",
        "btn_preview": "⚡ 15s-VORSCHAU",
        "btn_play": "⏯ PLAY/PAUSE",
        "meter_idle": "PEGELMESSER: Ungeprüft | Ziel für Shorts: -14 bis -11 dB",
        "vu_idle": "MITTELWERT: -- dB",
        "vu_fmt": "MITTEL: {mean:.1f} dB  |  SPITZE: {max:.1f} dB",
        "lvl_ok": "AUDIO-STATUS: OPTIMAL FÜR SHORTS",
        "lvl_low": "AUDIO-STATUS: ETWAS LEISE (Stimm-Gain erhöhen)",
        "lvl_high": "AUDIO-STATUS: ZU LAUT (Stimm-Gain senken)",
        "sec_09": "[ 09 // SYSTEMKONSOLE ]",
        "err_no_video": "[!] Bitte zuerst das Hauptvideo hineinziehen.",
        "err_no_tts": "[!] Keine TTS-Stimme zum Testen verfügbar.",
        "files_filter": "Dateien",
    },
}

BUILTIN_PRESETS = {
    "Locutor Pro (Recomendado)": {
        "eq_low": 55, "eq_lowmid": -40, "eq_mid": -20, "eq_pres": 45, "eq_high": 35,
        "voice_gain": 85, "comp_ratio": 40, "gate": 12, "music_db": -220,
        "ducking": True, "fx_deesser": True, "fx_exciter": True,
        "fx_warmth": True, "fx_dual_mono": True,
    },
    "Podcast Cálido": {
        "eq_low": 65, "eq_lowmid": -25, "eq_mid": -10, "eq_pres": 25, "eq_high": 20,
        "voice_gain": 75, "comp_ratio": 32, "gate": 10, "music_db": -240,
        "ducking": True, "fx_deesser": True, "fx_exciter": False,
        "fx_warmth": True, "fx_dual_mono": True,
    },
    "Plano (0 dB)": {
        "eq_low": 0, "eq_lowmid": 0, "eq_mid": 0, "eq_pres": 0, "eq_high": 0,
        "voice_gain": 60, "comp_ratio": 25, "gate": 10, "music_db": -220,
        "ducking": True, "fx_deesser": False, "fx_exciter": False,
        "fx_warmth": False, "fx_dual_mono": False,
    },
}

CYBERPUNK_QSS = """
QMainWindow, QWidget {
    background-color: #07090f;
    color: #d8f8ff;
    font-family: "JetBrains Mono", "Fira Code", "Noto Sans CJK JP", "Noto Sans Arabic", "DejaVu Sans Mono", monospace;
    font-size: 12px;
}
QScrollArea {
    border: none;
    background-color: #0d111c;
}
QScrollBar:vertical {
    background: #080b14;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #00a8b5;
    border-radius: 4px;
    min-height: 24px;
}
QFrame#HudPanel {
    background-color: #0d111c;
    border: 1px solid #00f3ff;
    border-radius: 6px;
}
QFrame#EqBox {
    background-color: #080b14;
    border: 1px solid #1e3a4c;
    border-radius: 5px;
}
QLabel#HeaderTitle {
    color: #00f3ff;
    font-size: 17px;
    font-weight: bold;
    letter-spacing: 1px;
}
QLabel#SectionTitle {
    color: #ff007f;
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 1px;
    border-bottom: 1px solid #3a1230;
    padding-bottom: 2px;
}
QLabel#DropZone {
    background-color: #090d16;
    border: 2px dashed #00a8b5;
    border-radius: 6px;
    color: #7eeeff;
    padding: 6px;
}
QLabel#DropZone[loaded="true"] {
    border: 2px solid #00ff9c;
    color: #00ff9c;
    background-color: #081814;
}
QPushButton {
    background-color: #101829;
    color: #00f3ff;
    border: 1px solid #00f3ff;
    border-radius: 4px;
    padding: 5px 9px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #00f3ff;
    color: #07090f;
}
QPushButton:disabled {
    border-color: #2c3547;
    color: #4b5a73;
    background-color: #0b0f18;
}
QPushButton#ActionRun {
    background-color: #240718;
    color: #ff007f;
    border: 2px solid #ff007f;
    font-size: 13px;
    padding: 9px;
}
QPushButton#ActionRun:hover {
    background-color: #ff007f;
    color: #07090f;
}
QPushButton#ActionPreview {
    background-color: #1d1a05;
    color: #fcee0a;
    border: 2px solid #fcee0a;
    padding: 8px;
}
QPushButton#ActionPreview:hover {
    background-color: #fcee0a;
    color: #07090f;
}
QLineEdit, QComboBox, QSpinBox {
    background-color: #080b12;
    color: #00ff9c;
    border: 1px solid #1e3a4c;
    border-radius: 4px;
    padding: 4px 6px;
}
QSlider::groove:horizontal {
    height: 6px;
    background: #141c2e;
    border: 1px solid #1f3d52;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    background: #00f3ff;
    border: 1px solid #ffffff;
    width: 14px;
    margin: -5px 0;
    border-radius: 3px;
}
QSlider::sub-page:horizontal {
    background: #ff007f;
    border-radius: 3px;
}
QSlider::groove:vertical {
    width: 6px;
    background: #141c2e;
    border: 1px solid #1f3d52;
    border-radius: 3px;
}
QSlider::handle:vertical {
    background: #00f3ff;
    border: 1px solid #ffffff;
    height: 14px;
    margin: 0 -5px;
    border-radius: 3px;
}
QSlider::add-page:vertical {
    background: #00ff9c;
    border-radius: 3px;
}
QProgressBar {
    background-color: #090d16;
    border: 1px solid #00f3ff;
    border-radius: 4px;
    text-align: center;
    color: #ffffff;
    font-weight: bold;
}
QProgressBar::chunk {
    background-color: #00ff9c;
}
QTextEdit {
    background-color: #05070c;
    color: #00ff9c;
    border: 1px solid #1a3344;
    border-radius: 4px;
    font-size: 11px;
}
QCheckBox {
    color: #fcee0a;
    spacing: 5px;
    font-size: 11px;
}
"""


# =====================================================================
# UTILIDADES DE AUDIO, VIDEO, SRT Y PULIDO GLOBAL DE DIÁLOGOS (2 PASADAS)
# =====================================================================

def count_audio_streams(file_path):
    try:
        cmd = [
            "ffprobe", "-v", "error", "-select_streams", "a",
            "-show_entries", "stream=index", "-of", "csv=p=0", file_path
        ]
        out = subprocess.check_output(cmd).decode().strip()
        return len(out.splitlines()) if out else 0
    except Exception:
        return 1


def get_media_duration(file_path):
    try:
        cmd = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(file_path)
        ]
        return float(subprocess.check_output(cmd).decode().strip())
    except Exception:
        return 0.0


def resolve_audio_map(video_path, track_choice):
    if track_choice == "auto":
        num = count_audio_streams(video_path)
        if num >= 3:
            return "0:a:2", f"Auto -> Track 3 / {num}"
        if num == 2:
            return "0:a:1", f"Auto -> Track 2 / {num}"
        return "0:a:0", f"Auto -> Track 1 / {num}"
    idx = int(track_choice)
    return f"0:a:{idx}", f"Manual -> Track {idx + 1}"


def get_font_for_lang(lang_code):
    return LANG_META.get(lang_code, LANG_META["es"])["font"]


def build_voice_filter(cfg):
    chain = []
    if cfg.get("fx_dual_mono", True):
        chain.append("aformat=channel_layouts=mono,pan=stereo|c0=c0|c1=c0")

    chain.extend([
        "highpass=f=75",
        "lowpass=f=14000",
        "afftdn=nr=12:nf=-40:tn=1",
        f"agate=threshold={cfg['gate']:.3f}:ratio=4:range=0.01:attack=10:release=250:knee=2",
        f"lowshelf=f=110:g={cfg['eq_low']:.1f}:t=q:w=0.7",
        f"equalizer=f=322:t=o:w=1.8:g={cfg['eq_lowmid']:.1f}",
        f"equalizer=f=837:t=o:w=1.0:g={cfg['eq_mid']:.1f}",
        f"equalizer=f=4800:t=o:w=1.2:g={cfg['eq_pres']:.1f}",
        f"highshelf=f=10000:g={cfg['eq_high']:.1f}:t=q:w=0.7",
    ])

    if cfg.get("fx_deesser", True):
        chain.append("deesser=i=0.45:m=0.5:f=0.5:s=o")

    chain.append(
        f"acompressor=threshold=0.06:ratio={cfg['comp_ratio']:.1f}:attack=5:release=90:makeup=2.5:knee=3"
    )

    if cfg.get("fx_exciter", True):
        chain.append("aexciter=level_in=1:level_out=1:amount=1.2:drive=4.5:blend=0:freq=7000:ceil=14000")

    chain.append(f"volume={cfg['voice_gain']:.1f}dB")

    if cfg.get("fx_warmth", True):
        chain.append("asoftclip=type=tanh:threshold=0.85")

    chain.append("alimiter=limit=0.92:attack=3:release=50:level=disabled")
    return ",".join(chain)


def build_tts_clean_filter():
    return ",".join([
        "aformat=channel_layouts=mono,pan=stereo|c0=c0|c1=c0",
        "highpass=f=75",
        "lowshelf=f=110:g=3.0:t=q:w=0.7",
        "equalizer=f=4500:t=o:w=1.2:g=2.0",
        "acompressor=threshold=0.08:ratio=3.0:attack=5:release=90:makeup=2.0:knee=3",
        "alimiter=limit=0.92:attack=3:release=50:level=disabled",
    ])


def build_atempo_chain(speed):
    parts = []
    while speed > 2.0:
        parts.append("atempo=2.0")
        speed /= 2.0
    while speed < 0.5:
        parts.append("atempo=0.5")
        speed /= 0.5
    parts.append(f"atempo={speed:.4f}")
    return ",".join(parts)


def detect_audio_levels(media_path):
    cmd = ["ffmpeg", "-i", media_path, "-af", "volumedetect", "-f", "null", "-"]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    mean_m = re.search(r"mean_volume:\s*([-\d.]+)\s*dB", proc.stderr)
    max_m = re.search(r"max_volume:\s*([-\d.]+)\s*dB", proc.stderr)
    mean_db = float(mean_m.group(1)) if mean_m else -60.0
    max_db = float(max_m.group(1)) if max_m else -60.0
    return mean_db, max_db


def format_srt_ts(seconds):
    ms = int(round((seconds - int(seconds)) * 1000))
    total_s = int(seconds)
    if ms >= 1000:
        total_s += 1
        ms -= 1000
    h = total_s // 3600
    m = (total_s % 3600) // 60
    s = total_s % 60
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def parse_srt_segments(srt_path):
    content = Path(srt_path).read_text(encoding="utf-8", errors="ignore")
    blocks = re.split(r"\r?\n\s*\r?\n", content.strip())
    ts_re = re.compile(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)")
    results = []
    for block in blocks:
        lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
        ts_idx = -1
        match = None
        for idx, ln in enumerate(lines):
            m = ts_re.search(ln)
            if m:
                ts_idx = idx
                match = m
                break
        if match and ts_idx + 1 < len(lines):
            h1, m1, s1, ms1, h2, m2, s2, ms2 = map(int, match.groups())
            start = h1 * 3600 + m1 * 60 + s1 + ms1 / 1000.0
            end = h2 * 3600 + m2 * 60 + s2 + ms2 / 1000.0
            txt = " ".join(lines[ts_idx + 1:]).strip()
            if txt:
                results.append((start, end, txt))
    return results


def write_srt_segments(srt_path, segments):
    entries = []
    for idx, (start, end, text) in enumerate(segments, 1):
        entries.append(f"{idx}\n{format_srt_ts(start)} --> {format_srt_ts(end)}\n{text.strip()}\n")
    Path(srt_path).write_text("\n".join(entries), encoding="utf-8")


def _analyze_full_transcript_with_ollama(segments, ollama_model, target_lang, context_path, log_fn=None):
    full_lines = [f"[{i}] {txt}" for i, (_, _, txt) in enumerate(segments)]
    full_text = "\n".join(full_lines)

    if len(full_text) > 42000:
        half = 20000
        full_text = (
            full_text[:half]
            + "\n...[MIDDLE SECTION OMITTED FOR LENGTH]...\n"
            + full_text[-half:]
        )

    lang_name = LANG_META.get(target_lang, LANG_META["es"])["prompt_name"]
    if log_fn:
        log_fn(f"[AI SCRIPT 1/2] Analyzing full transcript ({len(segments)} lines) -> Target: {lang_name}...")

    prompt_global = f"""You are a lead script editor and dubbing director.
Read this entire raw Whisper transcript and extract the global editorial map so the rewritten dialogue stays 100% coherent and technically accurate in {lang_name}.

Return EXCLUSIVELY a JSON object with this structure (values written in {lang_name}):
{{
  "main_topic": "What the video is about in 1-2 clear sentences",
  "core_message": "What the viewer should understand or achieve by the end",
  "tone_style": "e.g., practical tutorial, direct, first-person",
  "technical_glossary": [
    "Exact names of tools, commands, frameworks, platforms mentioned (fix obvious Whisper misspellings)"
  ],
  "narrative_arc": [
    "Stage 1 (intro): ...",
    "Stage 2 (main walkthrough): ...",
    "Stage 3 (closing): ..."
  ]
}}

Full transcript:
{full_text}
"""
    payload = {
        "model": ollama_model,
        "prompt": prompt_global,
        "stream": False,
        "format": "json",
        "options": {"num_ctx": 16384, "num_predict": 2048, "temperature": 0.15},
    }

    try:
        req = urllib.request.Request(
            OLLAMA_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=300) as resp:
            raw_resp = json.loads(resp.read().decode("utf-8")).get("response", "{}").strip()

        if raw_resp.startswith("```"):
            raw_resp = re.sub(r"^```(?:json)?\s*", "", raw_resp)
            raw_resp = re.sub(r"\s*```$", "", raw_resp)

        brief = json.loads(raw_resp)
        if isinstance(brief, dict):
            Path(context_path).write_text(
                json.dumps(brief, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            if log_fn:
                log_fn(f"[✓] Topic: {brief.get('main_topic', 'N/A')}")
                glos = brief.get("technical_glossary", [])
                if glos:
                    log_fn(f"[✓] Glossary: {', '.join(map(str, glos[:15]))}")
            return brief
    except Exception as exc:
        if log_fn:
            log_fn(f"[!] Could not generate global map ({exc}); continuing with local context.")

    return {}


def polish_srt_with_ollama(srt_path, ollama_model, target_lang, log_fn=None):
    raw_backup = srt_path.replace(".srt", "_raw.srt")
    context_path = srt_path.replace(".srt", "_contexto.json")

    if not os.path.exists(raw_backup):
        shutil.copy2(srt_path, raw_backup)

    segments = parse_srt_segments(raw_backup)
    if not segments:
        return segments

    lang_name = LANG_META.get(target_lang, LANG_META["es"])["prompt_name"]
    global_brief = _analyze_full_transcript_with_ollama(
        segments, ollama_model, target_lang, context_path, log_fn=log_fn
    )
    brief_json = json.dumps(global_brief, ensure_ascii=False, indent=2) if global_brief else "{}"

    polished = list(segments)
    chunk_size = 18

    for offset in range(0, len(segments), chunk_size):
        chunk = segments[offset:offset + chunk_size]
        if log_fn:
            log_fn(
                f"[AI SCRIPT 2/2] Polishing/adapting lines {offset + 1}-{offset + len(chunk)} / {len(segments)} ({target_lang})..."
            )

        prev_context = [txt for _, _, txt in polished[max(0, offset - 3):offset]]
        next_context = [txt for _, _, txt in segments[offset + len(chunk):offset + len(chunk) + 3]]

        items_for_prompt = [
            {
                "id": i,
                "dur_s": round(max(end - start, 0.3), 2),
                "words": len(txt.split()),
                "text": txt,
            }
            for i, (start, end, txt) in enumerate(chunk)
        ]

        prompt = f"""You are a dubbing director and technical scriptwriter fluent in {lang_name}.
Rewrite (and translate if the source is in a different language) ONLY "segments_to_polish" into natural, crystal-clear {lang_name}, keeping complete narrative coherence and lip-sync timing for TTS playback.

GLOBAL VIDEO MAP (coherence & terminology guide):
{brief_json}

PREVIOUS CONTEXT (already polished, reference ONLY — DO NOT output):
{json.dumps(prev_context, ensure_ascii=False)}

NEXT CONTEXT (upcoming raw lines, reference ONLY — DO NOT output):
{json.dumps(next_context, ensure_ascii=False)}

STRICT RULES:
1. OUTPUT LANGUAGE: Every rewritten line MUST be in {lang_name}.
2. MESSAGE COHERENCE: Fix Whisper transcription mistakes using the GLOBAL VIDEO MAP and surrounding context so technical explanations make complete sense.
3. SMOOTH CONTINUITY: Connect naturally from "PREVIOUS CONTEXT". If a sentence continues into the next segment or "NEXT CONTEXT", do not force an early period.
4. CLEAN DICTION: Remove filler words, stutters, and accidental repetitions. Use exact spellings from "technical_glossary".
5. LIP-SYNC TIMING: Keep spoken length closely matched to "dur_s" seconds (within roughly ±15% spoken duration) so the TTS matches mouth movement on screen.
6. Keep first-person natural tone. Return ALL IDs from "segments_to_polish" in exact order.

Return EXCLUSIVELY a JSON object:
{{
  "lines": [
    {{"id": 0, "text": "Polished and coherent line in {lang_name}."}}
  ]
}}

segments_to_polish:
{json.dumps(items_for_prompt, ensure_ascii=False, indent=2)}
"""
        payload = {
            "model": ollama_model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {"num_ctx": 16384, "num_predict": 4096, "temperature": 0.15},
        }
        try:
            req = urllib.request.Request(
                OLLAMA_URL,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=240) as resp:
                raw_resp = json.loads(resp.read().decode("utf-8")).get("response", "{}").strip()

            if raw_resp.startswith("```"):
                raw_resp = re.sub(r"^```(?:json)?\s*", "", raw_resp)
                raw_resp = re.sub(r"\s*```$", "", raw_resp)

            parsed = json.loads(raw_resp)
            lines_list = parsed.get("lines", parsed) if isinstance(parsed, dict) else parsed

            if isinstance(lines_list, list):
                for item in lines_list:
                    if isinstance(item, dict) and "id" in item:
                        idx_local = int(item["id"])
                        new_txt = str(item.get("text", item.get("texto", ""))).strip()
                        if 0 <= idx_local < len(chunk) and new_txt:
                            s, e, _ = chunk[idx_local]
                            polished[offset + idx_local] = (s, e, new_txt)
        except Exception as exc:
            if log_fn:
                log_fn(f"[!] Warning in block {offset + 1}: keeping original text ({exc})")

    write_srt_segments(srt_path, polished)
    return polished


# =====================================================================
# DETECCIÓN AUTOMÁTICA DE VOCES CLONADAS (F5-TTS SOCKET) Y OTROS TTS
# =====================================================================

def _scan_shell_voice_aliases():
    script_to_alias = {}
    home = Path.home()

    fish_dir = home / ".config" / "fish" / "functions"
    if fish_dir.exists():
        for fish_file in sorted(fish_dir.glob("*.fish")):
            try:
                content = fish_file.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            m_py = re.search(r"python3?\s+([^\s\"';]+\.py)", content)
            if m_py:
                raw_path = os.path.expanduser(m_py.group(1).replace("$HOME", str(home)))
                resolved = str(Path(raw_path).resolve()) if os.path.exists(raw_path) else raw_path
                if "tts" in fish_file.stem.lower() or "tts" in resolved.lower() or "voz" in resolved.lower():
                    script_to_alias[resolved] = fish_file.stem

    for rc_name in (".bashrc", ".zshrc"):
        rc_path = home / rc_name
        if not rc_path.exists():
            continue
        try:
            content = rc_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for m in re.finditer(r"alias\s+([a-zA-Z0-9_-]+)\s*=\s*[\"'][^\"']*python3?\s+([^\s\"']+\.py)", content):
            alias_name = m.group(1)
            raw_path = os.path.expanduser(m.group(2).replace("$HOME", str(home)))
            resolved = str(Path(raw_path).resolve()) if os.path.exists(raw_path) else raw_path
            if "tts" in alias_name.lower() or "tts" in resolved.lower() or "voz" in resolved.lower():
                script_to_alias.setdefault(resolved, alias_name)

    return script_to_alias


def discover_tts_voices():
    voices = []
    home = Path.home()
    script_aliases = _scan_shell_voice_aliases()
    seen_scripts = set()
    seen_socks = set()

    candidate_scripts = []
    for sp in script_aliases:
        if os.path.exists(sp):
            candidate_scripts.append(Path(sp))

    local_bin = home / ".local" / "bin"
    if local_bin.exists():
        for pyf in sorted(local_bin.glob("*.py")):
            candidate_scripts.append(pyf)

    for script in candidate_scripts:
        try:
            resolved = str(script.resolve())
        except Exception:
            continue
        if resolved in seen_scripts or not os.path.exists(resolved):
            continue

        try:
            code = Path(resolved).read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        alias_name = script_aliases.get(resolved, script.stem)
        is_tts_name = (
            "tts" in script.stem.lower()
            or "voz" in script.stem.lower()
            or resolved in script_aliases
        )

        m_sock = re.search(r'SOCK\s*=\s*["\']([^"\']+\.sock)["\']', code)
        is_f5_daemon = bool(
            m_sock and ("--daemon" in code or "AF_UNIX" in code or "f5_tts" in code)
        )

        if is_f5_daemon:
            seen_scripts.add(resolved)
            sock_path = m_sock.group(1)
            seen_socks.add(sock_path)
            running_tag = " ●RAM" if os.path.exists(sock_path) else ""
            voices.append({
                "id": f"f5_daemon::{alias_name}::{sock_path}",
                "label": f"🔥 Clone TTS: {alias_name} ({os.path.basename(sock_path)}{running_tag})",
                "engine": "f5_daemon",
                "target": resolved,
                "sock": sock_path,
            })
        elif is_tts_name:
            seen_scripts.add(resolved)
            voices.append({
                "id": f"custom_script::{alias_name}",
                "label": f"🎙 Local TTS Script: {alias_name}",
                "engine": "custom_script",
                "target": resolved,
            })

    for sock_file in sorted(Path("/tmp").glob("tts*.sock")):
        sp = str(sock_file)
        if sp not in seen_socks:
            seen_socks.add(sp)
            voices.append({
                "id": f"f5_daemon_live::{sock_file.stem}",
                "label": f"🔥 Live TTS Daemon: {sock_file.stem} (●RAM)",
                "engine": "f5_daemon",
                "target": None,
                "sock": sp,
            })

    piper_bin = shutil.which("piper") or shutil.which("piper-tts")
    if piper_bin:
        search_dirs = [
            home / ".local" / "share" / "piper",
            home / ".local" / "share" / "piper-voices",
            home / "piper",
            home / "Escritorio",
            home / "Desktop",
            Path("/usr/share/piper-voices"),
        ]
        found_onnx = set()
        for d in search_dirs:
            if d.exists():
                for onnx in d.rglob("*.onnx"):
                    resolved = str(onnx.resolve())
                    if resolved not in found_onnx:
                        found_onnx.add(resolved)
                        voices.append({
                            "id": f"piper::{onnx.stem}",
                            "label": f"🤖 Piper ({onnx.stem})",
                            "engine": "piper",
                            "target": resolved,
                            "bin": piper_bin,
                        })

    if shutil.which("edge-tts") or importlib.util.find_spec("edge_tts"):
        edge_list = [
            ("es-MX-JorgeNeural", "🌐 Edge-TTS [ES] Jorge (MX)"),
            ("es-MX-DaliaNeural", "🌐 Edge-TTS [ES] Dalia (MX)"),
            ("en-US-AndrewNeural", "🌐 Edge-TTS [EN] Andrew (US)"),
            ("en-US-AvaNeural", "🌐 Edge-TTS [EN] Ava (US)"),
            ("ja-JP-KeitaNeural", "🌐 Edge-TTS [JA] Keita (JP)"),
            ("ja-JP-NanamiNeural", "🌐 Edge-TTS [JA] Nanami (JP)"),
            ("it-IT-DiegoNeural", "🌐 Edge-TTS [IT] Diego (IT)"),
            ("it-IT-ElsaNeural", "🌐 Edge-TTS [IT] Elsa (IT)"),
            ("ar-SA-HamedNeural", "🌐 Edge-TTS [AR] Hamed (SA)"),
            ("ar-EG-SalmaNeural", "🌐 Edge-TTS [AR] Salma (EG)"),
            ("de-DE-ConradNeural", "🌐 Edge-TTS [DE] Conrad (DE)"),
            ("de-DE-KatjaNeural", "🌐 Edge-TTS [DE] Katja (DE)"),
        ]
        for code, label in edge_list:
            voices.append({
                "id": f"edge_tts::{code}",
                "label": label,
                "engine": "edge_tts",
                "target": code,
            })

    espeak_bin = shutil.which("espeak-ng") or shutil.which("espeak")
    if espeak_bin:
        for code, label in (
            ("es-419", "🔊 eSpeak [ES] Español"),
            ("en-us", "🔊 eSpeak [EN] English"),
            ("ja", "🔊 eSpeak [JA] 日本語"),
            ("it", "🔊 eSpeak [IT] Italiano"),
            ("ar", "🔊 eSpeak [AR] العربية"),
            ("de", "🔊 eSpeak [DE] Deutsch"),
        ):
            voices.append({
                "id": f"espeak::{code}",
                "label": label,
                "engine": "espeak",
                "target": code,
                "bin": espeak_bin,
            })

    return voices


def synthesize_tts_line(voice_info, text, out_wav, lang="es", log_fn=None):
    text = text.strip()
    if not text:
        return False

    engine = voice_info["engine"]
    out_wav = str(out_wav)

    if engine == "f5_daemon":
        sock_path = voice_info["sock"]
        script_path = voice_info.get("target")

        def _send():
            c = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            c.settimeout(300.0)
            c.connect(sock_path)
            payload = {"text": text, "out": out_wav, "lang": lang}
            c.sendall(json.dumps(payload).encode("utf-8"))
            resp = c.recv(4096).decode("utf-8")
            c.close()
            return resp

        try:
            res = _send()
        except Exception:
            if not script_path or not os.path.exists(script_path):
                raise RuntimeError(f"Socket {sock_path} unreachable and daemon script not found.")
            if log_fn:
                log_fn(f"[TTS] ⚡ Starting RAM daemon ({os.path.basename(script_path)} -> {sock_path})...")
            subprocess.Popen(
                [sys.executable, script_path, "--daemon"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            res = None
            for _ in range(180):
                time.sleep(0.5)
                if os.path.exists(sock_path):
                    try:
                        res = _send()
                        break
                    except Exception:
                        pass
            if res is None:
                raise RuntimeError(f"Timeout starting TTS daemon ({sock_path}).")

        if res != "OK":
            raise RuntimeError(f"TTS daemon error: {res}")
        return os.path.exists(out_wav)

    if engine == "custom_script":
        subprocess.run(
            [sys.executable, voice_info["target"], text, out_wav],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True
        )
        return os.path.exists(out_wav)

    if engine == "piper":
        subprocess.run(
            [voice_info["bin"], "--model", voice_info["target"], "--output_file", out_wav],
            input=text.encode("utf-8"),
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True
        )
        return os.path.exists(out_wav)

    if engine == "edge_tts":
        tmp_mp3 = out_wav + ".mp3"
        cmd = (
            ["edge-tts", "--voice", voice_info["target"], "--text", text, "--write-media", tmp_mp3]
            if shutil.which("edge-tts")
            else [sys.executable, "-m", "edge_tts", "--voice", voice_info["target"], "--text", text, "--write-media", tmp_mp3]
        )
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        subprocess.run(
            ["ffmpeg", "-y", "-i", tmp_mp3, "-ar", "48000", "-ac", "1", out_wav],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True
        )
        if os.path.exists(tmp_mp3):
            os.remove(tmp_mp3)
        return os.path.exists(out_wav)

    if engine == "espeak":
        subprocess.run(
            [voice_info["bin"], "-v", voice_info["target"], "-w", out_wav, text],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True
        )
        return os.path.exists(out_wav)

    raise RuntimeError(f"Unsupported TTS engine: {engine}")


def build_tts_timeline_wav(srt_path, total_duration, voice_info, out_wav, lang="es", lipsync_strict=True, log_fn=None):
    segments = parse_srt_segments(srt_path)
    if not segments:
        raise RuntimeError("No subtitles found in SRT to synthesize.")

    sample_rate = 48000
    total_samples = max(int((total_duration + 1.0) * sample_rate), sample_rate)
    timeline = array.array("h", [0]) * total_samples

    with tempfile.TemporaryDirectory(prefix="cyber_tts_") as tmpdir:
        for i, (start, end, text) in enumerate(segments):
            if log_fn and (i == 0 or (i + 1) % 5 == 0 or i + 1 == len(segments)):
                log_fn(f"[TTS/{lang}] {i + 1}/{len(segments)} ({start:.1f}s-{end:.1f}s): {text[:52]}")

            seg_raw = os.path.join(tmpdir, f"raw_{i:04d}.wav")
            seg_trim = os.path.join(tmpdir, f"trim_{i:04d}.wav")

            ok = synthesize_tts_line(voice_info, text, seg_raw, lang=lang, log_fn=log_fn)
            if not ok:
                continue

            trim_af = (
                "silenceremove=start_periods=1:start_threshold=-45dB,"
                "areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse"
            )
            subprocess.run(
                ["ffmpeg", "-y", "-i", seg_raw, "-af", trim_af, "-ar", str(sample_rate), "-ac", "1", seg_trim],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            src_seg = seg_trim if (os.path.exists(seg_trim) and get_media_duration(seg_trim) > 0.08) else seg_raw
            clean_dur = get_media_duration(src_seg)
            if clean_dur <= 0.05:
                continue

            mouth_dur = max(end - start, 0.25)
            next_start = segments[i + 1][0] if i + 1 < len(segments) else total_duration
            max_slot = max(next_start - start - 0.04, mouth_dur)

            speed = 1.0
            af_final = []
            if lipsync_strict:
                desired_speed = clean_dur / mouth_dur
                if clean_dur > max_slot:
                    min_needed = clean_dur / max_slot
                    speed = min(max(desired_speed, min_needed), 1.55)
                else:
                    speed = max(0.88, min(desired_speed, 1.38))
                if abs(speed - 1.0) > 0.04:
                    af_final.append(build_atempo_chain(speed))
                else:
                    speed = 1.0
            else:
                if clean_dur > max_slot:
                    speed = min(clean_dur / max_slot, 1.40)
                    if speed > 1.03:
                        af_final.append(build_atempo_chain(speed))
                    else:
                        speed = 1.0

            est_dur = clean_dur / speed
            fade_out_st = max(est_dur - 0.01, 0.01)
            af_final.append(f"afade=t=in:d=0.008,afade=t=out:st={fade_out_st:.3f}:d=0.008")

            pcm_cmd = [
                "ffmpeg", "-y", "-i", src_seg,
                "-af", ",".join(af_final),
                "-f", "s16le", "-acodec", "pcm_s16le",
                "-ar", str(sample_rate), "-ac", "1", "pipe:1"
            ]
            proc = subprocess.run(pcm_cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            if not proc.stdout:
                continue

            seg_samples = array.array("h")
            seg_samples.frombytes(proc.stdout)

            offset = int(start * sample_rate)
            needed = offset + len(seg_samples)
            if needed > len(timeline):
                timeline.extend([0] * (needed - len(timeline)))

            for j, val in enumerate(seg_samples):
                idx = offset + j
                mixed = timeline[idx] + val
                if mixed > 32767:
                    mixed = 32767
                elif mixed < -32768:
                    mixed = -32768
                timeline[idx] = mixed

    with wave.open(out_wav, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(timeline.tobytes())

    return out_wav


# =====================================================================
# WIDGETS Y WORKERS
# =====================================================================

class DropZone(QLabel):
    file_dropped = pyqtSignal(str)

    def __init__(self, title, hint, extensions, filter_label="Files", parent=None):
        super().__init__(parent)
        self.default_title = title
        self.hint_text = hint
        self.filter_label = filter_label
        self.extensions = extensions
        self.file_path = None
        self.setObjectName("DropZone")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setAcceptDrops(True)
        self.setWordWrap(True)
        self.setMinimumHeight(42)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._refresh_label()

    def set_texts(self, title, hint, filter_label):
        self.default_title = title
        self.hint_text = hint
        self.filter_label = filter_label
        self._refresh_label()

    def _refresh_label(self):
        if self.file_path:
            self.setText(f"✓ {os.path.basename(self.file_path)}")
        else:
            self.setText(f"{self.default_title}  {self.hint_text}")

    def set_file(self, path):
        if path and os.path.exists(path):
            self.file_path = path
            self.setProperty("loaded", True)
            self.style().unpolish(self)
            self.style().polish(self)
            self._refresh_label()
            self.setToolTip(path)
            self.file_dropped.emit(path)

    def clear_file(self):
        self.file_path = None
        self.setProperty("loaded", False)
        self.style().unpolish(self)
        self.style().polish(self)
        self._refresh_label()
        self.setToolTip("")

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if not urls:
            return
        path = urls[0].toLocalFile()
        if any(path.lower().endswith(ext) for ext in self.extensions):
            self.set_file(path)

    def mousePressEvent(self, event):
        ext_filter = f"{self.filter_label} (" + " ".join(f"*{e}" for e in self.extensions) + ")"
        path, _ = QFileDialog.getOpenFileName(self, self.default_title, "", ext_filter)
        if path:
            self.set_file(path)


class TtsTestWorker(QThread):
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)

    def __init__(self, voice_info, out_wav, lang):
        super().__init__()
        self.voice_info = voice_info
        self.out_wav = out_wav
        self.lang = lang

    def run(self):
        try:
            sample = LANG_META.get(self.lang, LANG_META["es"])["sample"]
            synthesize_tts_line(
                self.voice_info, sample, self.out_wav, lang=self.lang, log_fn=self.log_signal.emit
            )
            self.finished_signal.emit(self.out_wav)
        except Exception as exc:
            self.error_signal.emit(str(exc))


class PreviewWorker(QThread):
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(str, float, float)
    error_signal = pyqtSignal(str)

    def __init__(self, video_path, music_path, cfg, out_path):
        super().__init__()
        self.video_path = video_path
        self.music_path = music_path
        self.cfg = cfg
        self.out_path = out_path

    def run(self):
        try:
            audio_map, desc = resolve_audio_map(self.video_path, self.cfg["track"])
            self.log_signal.emit(f"[PREVIEW] Track: {audio_map} ({desc})")
            voice_chain = build_voice_filter(self.cfg)
            start_s = str(self.cfg["preview_start"])

            if self.music_path and os.path.exists(self.music_path):
                if self.cfg["ducking"]:
                    fc = (
                        f"[{audio_map}]{voice_chain},asetpts=PTS-STARTPTS,asplit=2[v_main][v_sc];"
                        f"[1:a]asetpts=PTS-STARTPTS,volume={self.cfg['music_db']:.1f}dB[m_lvl];"
                        f"[m_lvl][v_sc]sidechaincompress=threshold=0.02:ratio=6:attack=20:release=350[m_duck];"
                        f"[v_main][m_duck]amix=inputs=2:duration=first:dropout_transition=2:normalize=0,"
                        f"alimiter=limit=0.92:attack=3:release=50:level=disabled[aout]"
                    )
                else:
                    fc = (
                        f"[{audio_map}]{voice_chain},asetpts=PTS-STARTPTS[v_main];"
                        f"[1:a]asetpts=PTS-STARTPTS,volume={self.cfg['music_db']:.1f}dB[m_lvl];"
                        f"[v_main][m_lvl]amix=inputs=2:duration=first:dropout_transition=2:normalize=0,"
                        f"alimiter=limit=0.92:attack=3:release=50:level=disabled[aout]"
                    )

                cmd = [
                    "ffmpeg", "-y",
                    "-ss", start_s, "-t", "15", "-i", self.video_path,
                    "-stream_loop", "-1", "-i", self.music_path,
                    "-filter_complex", fc,
                    "-map", "0:v:0", "-map", "[aout]",
                    "-c:v", "libx264", "-preset", "ultrafast", "-crf", "26",
                    "-vf", "scale='min(960,iw)':-2",
                    "-c:a", "aac", "-b:a", "192k",
                    "-shortest", self.out_path
                ]
            else:
                cmd = [
                    "ffmpeg", "-y",
                    "-ss", start_s, "-t", "15", "-i", self.video_path,
                    "-map", "0:v:0", "-map", audio_map,
                    "-af", voice_chain,
                    "-c:v", "libx264", "-preset", "ultrafast", "-crf", "26",
                    "-vf", "scale='min(960,iw)':-2",
                    "-c:a", "aac", "-b:a", "192k",
                    self.out_path
                ]

            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if proc.returncode != 0:
                raise RuntimeError(proc.stderr[-800:])

            mean_db, max_db = detect_audio_levels(self.out_path)
            self.finished_signal.emit(self.out_path, mean_db, max_db)
        except Exception as exc:
            self.error_signal.emit(str(exc))


class PipelineWorker(QThread):
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)

    def __init__(self, video_base, video_extra, music_path, cfg, tts_voice):
        super().__init__()
        self.video_base = video_base
        self.video_extra = video_extra
        self.music_path = music_path
        self.cfg = cfg
        self.tts_voice = tts_voice

    def run_cmd(self, cmd, cwd=None):
        proc = subprocess.Popen(
            cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )
        for line in proc.stdout:
            clean = line.strip()
            if clean:
                self.log_signal.emit(clean)
        proc.wait()
        if proc.returncode != 0:
            raise RuntimeError(f"Command failed ({proc.returncode}): {' '.join(cmd[:4])}")

    def run(self):
        try:
            work_dir = os.path.dirname(os.path.abspath(self.video_base))
            out_dir = self.cfg["out_dir"]
            os.makedirs(out_dir, exist_ok=True)

            src_lang = self.cfg["source_lang"]
            target_lang = self.cfg["target_lang"]
            target_lang_name = LANG_META.get(target_lang, LANG_META["es"])["prompt_name"]
            font_name = get_font_for_lang(target_lang)

            video_prepared = os.path.join(work_dir, "unido.mp4")
            video_voice_cut = os.path.join(work_dir, "_tmp_altered_voice.mp4")
            video_tts_cut = os.path.join(work_dir, "_tmp_altered_tts.mp4")
            video_clean = os.path.join(work_dir, "video_ALTERED.mp4")
            video_vertical = os.path.join(work_dir, "video_ALTERED_VERTICAL.mp4")
            srt_output = os.path.join(work_dir, "video_ALTERED.srt")
            srt_raw_backup = os.path.join(work_dir, "video_ALTERED_raw.srt")
            srt_context_json = os.path.join(work_dir, "video_ALTERED_contexto.json")

            if self.cfg["force_reprocess"]:
                for f in (
                    video_prepared, video_voice_cut, video_tts_cut,
                    video_clean, video_vertical, srt_output,
                    srt_raw_backup, srt_context_json
                ):
                    if os.path.exists(f):
                        os.remove(f)
                        self.log_signal.emit(f"[*] Cache cleared: {os.path.basename(f)}")

            # =========================================================
            # [0/7] UNIÓN Y MASTERIZACIÓN DE VOZ LIMPIA
            # =========================================================
            self.log_signal.emit("\n" + "=" * 58)
            self.log_signal.emit("[0/7] Merging & mastering clean voice...")
            self.log_signal.emit("=" * 58)
            self.progress_signal.emit(8)

            audio_map, desc = resolve_audio_map(self.video_base, self.cfg["track"])
            self.log_signal.emit(f"[*] Audio: {audio_map} ({desc})")
            voice_filter = build_voice_filter(self.cfg)

            if not os.path.exists(video_prepared) and not os.path.exists(video_voice_cut) and not os.path.exists(video_clean):
                if self.video_extra and os.path.exists(self.video_extra):
                    lista_txt = os.path.join(work_dir, "lista_unir.txt")
                    p1 = self.video_base.replace("'", "'\\''")
                    p2 = self.video_extra.replace("'", "'\\''")
                    with open(lista_txt, "w", encoding="utf-8") as f:
                        f.write(f"file '{p1}'\nfile '{p2}'\n")
                    cmd = [
                        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                        "-i", lista_txt,
                        "-map", "0:v:0", "-map", audio_map,
                        "-c:v", "copy",
                        "-af", voice_filter,
                        "-c:a", "aac", "-b:a", "192k",
                        video_prepared
                    ]
                    self.run_cmd(cmd, cwd=work_dir)
                    os.remove(lista_txt)
                else:
                    cmd = [
                        "ffmpeg", "-y", "-i", self.video_base,
                        "-map", "0:v:0", "-map", audio_map,
                        "-c:v", "copy",
                        "-af", voice_filter,
                        "-c:a", "aac", "-b:a", "192k",
                        video_prepared
                    ]
                    self.run_cmd(cmd, cwd=work_dir)
            else:
                self.log_signal.emit("[!] Reusing existing intermediate file.")

            # =========================================================
            # [1/7] CORTE DE SILENCIOS CON AUTO-EDITOR
            # =========================================================
            self.log_signal.emit("\n" + "=" * 58)
            self.log_signal.emit("[1/7] Cutting silences (>5s) with auto-editor...")
            self.log_signal.emit("=" * 58)
            self.progress_signal.emit(16)

            if not os.path.exists(video_clean):
                input_ae = video_prepared if os.path.exists(video_prepared) else self.video_base
                if not os.path.exists(video_voice_cut):
                    self.run_cmd([
                        "auto-editor", input_ae,
                        "--edit", "audio:threshold=4%,mincut=5s",
                        "-o", video_voice_cut
                    ], cwd=work_dir)
                else:
                    self.log_signal.emit("[!] Reusing _tmp_altered_voice.mp4.")
            else:
                self.log_signal.emit("[!] Reusing existing video_ALTERED.mp4.")

            # =========================================================
            # [2/7] TRANSCRIPCIÓN PRECISA CON FASTER-WHISPER
            # =========================================================
            self.log_signal.emit("\n" + "=" * 58)
            self.log_signal.emit(f"[2/7] Transcribing with Faster-Whisper (source={src_lang})...")
            self.log_signal.emit("=" * 58)
            self.progress_signal.emit(26)

            src_for_whisper = video_voice_cut if os.path.exists(video_voice_cut) else video_clean
            if not os.path.exists(srt_output):
                from faster_whisper import WhisperModel
                model = WhisperModel("small", device="cpu", compute_type="int8")
                w_kw = {"word_timestamps": True}
                if src_lang != "auto":
                    w_kw["language"] = src_lang
                try:
                    segments, info = model.transcribe(src_for_whisper, vad_filter=True, **w_kw)
                except Exception:
                    segments, info = model.transcribe(src_for_whisper, **w_kw)

                srt_segs = []
                for seg in segments:
                    txt = seg.text.strip()
                    if not txt:
                        continue
                    if getattr(seg, "words", None):
                        real_start = seg.words[0].start
                        real_end = seg.words[-1].end
                    else:
                        real_start = seg.start
                        real_end = seg.end
                    srt_segs.append((real_start, max(real_end, real_start + 0.2), txt))

                write_srt_segments(srt_output, srt_segs)
                det = getattr(info, "language", src_lang)
                self.log_signal.emit(f"[✓] SRT generated: {len(srt_segs)} lines (detected: {det}).")
            else:
                self.log_signal.emit("[!] Reusing existing video_ALTERED.srt.")

            # =========================================================
            # [3/7] PULIDO / TRADUCCIÓN GLOBAL CON OLLAMA (2 PASADAS)
            # =========================================================
            if self.cfg["polish_dialogue"]:
                self.log_signal.emit("\n" + "=" * 58)
                self.log_signal.emit(
                    f"[3/7] Global context & dialogue polishing ({target_lang_name}) via {self.cfg['ollama_model']}..."
                )
                self.log_signal.emit("=" * 58)
                self.progress_signal.emit(36)
                polish_srt_with_ollama(
                    srt_output, self.cfg["ollama_model"], target_lang, log_fn=self.log_signal.emit
                )
                self.log_signal.emit("[✓] Coherent dialogues saved to video_ALTERED.srt.")
            else:
                self.log_signal.emit("\n[3/7] Ollama dialogue polishing skipped.")

            srt_text_dump = []
            for start_s, _, txt in parse_srt_segments(srt_output):
                t_clean = f"{int(start_s//3600):02d}:{int((start_s%3600)//60):02d}:{int(start_s%60):02d}"
                srt_text_dump.append(f"[{t_clean}] {txt}")

            # =========================================================
            # [4/7] REGRABACIÓN DE VOZ CON TTS + SINCRONÍA LABIAL
            # =========================================================
            voice_master_video = video_voice_cut
            if not os.path.exists(video_clean) and self.cfg["use_tts"]:
                if not self.tts_voice:
                    raise RuntimeError("TTS voice re-recording enabled, but no voice is selected.")
                self.log_signal.emit("\n" + "=" * 58)
                self.log_signal.emit(f"[4/7] Re-recording synced voice ({target_lang}): {self.tts_voice['label']}...")
                self.log_signal.emit("=" * 58)
                self.progress_signal.emit(48)

                dur = get_media_duration(video_voice_cut)
                tts_raw_wav = os.path.join(work_dir, "_tmp_tts_timeline.wav")
                build_tts_timeline_wav(
                    srt_output,
                    dur,
                    self.tts_voice,
                    tts_raw_wav,
                    lang=target_lang,
                    lipsync_strict=self.cfg["lipsync_strict"],
                    log_fn=self.log_signal.emit,
                )

                tts_af = voice_filter if self.cfg["tts_apply_rack"] else build_tts_clean_filter()
                cmd_swap = [
                    "ffmpeg", "-y",
                    "-i", video_voice_cut,
                    "-i", tts_raw_wav,
                    "-map", "0:v:0", "-map", "1:a:0",
                    "-c:v", "copy",
                    "-af", tts_af,
                    "-c:a", "aac", "-b:a", "192k",
                    "-shortest",
                    video_tts_cut
                ]
                self.run_cmd(cmd_swap, cwd=work_dir)
                if os.path.exists(tts_raw_wav):
                    os.remove(tts_raw_wav)
                voice_master_video = video_tts_cut
            else:
                self.log_signal.emit("\n[4/7] TTS re-recording disabled (keeping original voice).")

            # =========================================================
            # [5/7] INTEGRAR MÚSICA EN video_ALTERED.mp4 (HORIZONTAL)
            # =========================================================
            self.log_signal.emit("\n" + "=" * 58)
            self.log_signal.emit("[5/7] Building final video_ALTERED.mp4 (Horizontal + music)...")
            self.log_signal.emit("=" * 58)
            self.progress_signal.emit(58)

            has_music = bool(self.music_path and os.path.exists(self.music_path))
            if not os.path.exists(video_clean):
                if has_music:
                    if self.cfg["ducking"]:
                        mix_fc = (
                            "[0:a:0]asetpts=PTS-STARTPTS,asplit=2[v_main][v_sc];"
                            f"[1:a]asetpts=PTS-STARTPTS,volume={self.cfg['music_db']:.1f}dB,afade=t=in:d=0.6[m_lvl];"
                            "[m_lvl][v_sc]sidechaincompress=threshold=0.02:ratio=6:attack=20:release=350[m_duck];"
                            "[v_main][m_duck]amix=inputs=2:duration=first:dropout_transition=2:normalize=0,"
                            "alimiter=limit=0.92:attack=3:release=50:level=disabled[aout]"
                        )
                    else:
                        mix_fc = (
                            "[0:a:0]asetpts=PTS-STARTPTS[v_main];"
                            f"[1:a]asetpts=PTS-STARTPTS,volume={self.cfg['music_db']:.1f}dB,afade=t=in:d=0.6[m_lvl];"
                            "[v_main][m_lvl]amix=inputs=2:duration=first:dropout_transition=2:normalize=0,"
                            "alimiter=limit=0.92:attack=3:release=50:level=disabled[aout]"
                        )
                    cmd_mix = [
                        "ffmpeg", "-y",
                        "-i", voice_master_video,
                        "-stream_loop", "-1", "-i", self.music_path,
                        "-filter_complex", mix_fc,
                        "-map", "0:v:0", "-map", "[aout]",
                        "-c:v", "copy",
                        "-c:a", "aac", "-b:a", "192k",
                        "-shortest",
                        video_clean
                    ]
                    self.run_cmd(cmd_mix, cwd=work_dir)
                else:
                    shutil.move(voice_master_video, video_clean)

                for tmpf in (video_voice_cut, video_tts_cut):
                    if os.path.exists(tmpf):
                        os.remove(tmpf)

            self.log_signal.emit(f"[✓] Full horizontal video ready: {video_clean}")

            # =========================================================
            # [6/7] GENERAR VIDEO COMPLETO EN VERTICAL (1080x1920)
            # =========================================================
            srt_rel = os.path.basename(srt_output)
            if self.cfg["gen_full_vertical"]:
                self.log_signal.emit("\n" + "=" * 58)
                self.log_signal.emit("[6/7] Rendering full VERTICAL video (1080x1920)...")
                self.log_signal.emit("=" * 58)
                self.progress_signal.emit(68)

                if not os.path.exists(video_vertical):
                    full_vert_fc = (
                        "[0:v]split=2[bg][fg];"
                        "[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,avgblur=30[bg_b];"
                        "[fg]scale=1080:-1[fg_s];"
                        "[bg_b][fg_s]overlay=(W-w)/2:(H-h)/2,"
                        f"subtitles='{srt_rel}':force_style='PlayResX=1080,PlayResY=1920,FontSize=42,FontName={font_name},Bold=1,PrimaryColour=&H0000FFFF,OutlineColour=&H00000000,BackColour=&H80000000,BorderStyle=1,Outline=3,Shadow=2,Alignment=2,MarginV=180'[v]"
                    )
                    cmd_vert = [
                        "ffmpeg", "-y",
                        "-i", video_clean,
                        "-filter_complex", full_vert_fc,
                        "-map", "[v]", "-map", "0:a:0",
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                        "-c:a", "copy",
                        video_vertical
                    ]
                    self.run_cmd(cmd_vert, cwd=work_dir)
                self.log_signal.emit(f"[✓] Full vertical video ready: {video_vertical}")
            else:
                self.log_signal.emit("\n[6/7] Full vertical video skipped.")

            # =========================================================
            # [7/7] OLLAMA + CORTE DE SHORTS DIRECTO DE video_ALTERED.mp4
            # =========================================================
            self.log_signal.emit("\n" + "=" * 58)
            self.log_signal.emit(f"[7/7] Extracting 10-15 shorts ({target_lang_name}) via {self.cfg['ollama_model']}...")
            self.log_signal.emit("=" * 58)
            self.progress_signal.emit(76)

            prompt_analysis = f"""You are a professional vertical video editor (YouTube Shorts / TikTok / Reels).
Analyze the entire transcript carefully and extract MANDATORILY between 10 and 15 key viral moments.

CRITICAL INSTRUCTIONS:
1. Mandatory quota: minimum 10 clips, maximum 15 clips. DO NOT return fewer than 10.
2. Each clip must last between 30 and 75 seconds.
3. Cover the ENTIRE video: start, middle, and end.
4. Timestamp format: "HH:MM:SS" (strict).
5. Titles & descriptions MUST be written in {target_lang_name}. Titles should be short, punchy (UPPERCASE if Latin script), without colons or quotes.
6. Field "filename": ASCII alphanumeric with underscores (e.g. "01_SHORT_TITLE", "02_SHORT_TITLE").

Return EXCLUSIVELY a JSON array:
[
  {{
    "start": "00:00:45",
    "end": "00:01:35",
    "filename": "01_CLIP_SUMMARY",
    "title": "SHORT PUNCHY TITLE",
    "desc": "Short metadata description in {target_lang_name}"
  }}
]

Transcript:
{chr(10).join(srt_text_dump)}
"""
            payload = {
                "model": self.cfg["ollama_model"],
                "prompt": prompt_analysis,
                "stream": False,
                "format": "json",
                "options": {"num_ctx": 16384, "num_predict": 4096, "temperature": 0.2},
            }
            req = urllib.request.Request(
                OLLAMA_URL,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req) as resp:
                raw_response = json.loads(resp.read().decode("utf-8")).get("response", "[]").strip()

            if raw_response.startswith("```"):
                raw_response = re.sub(r"^```(?:json)?\s*", "", raw_response)
                raw_response = re.sub(r"\s*```$", "", raw_response)

            parsed = json.loads(raw_response)
            clips = parsed.get("clips", parsed) if isinstance(parsed, dict) else parsed
            self.log_signal.emit(f"[✓] AI detected {len(clips)} shorts. Slicing directly from video_ALTERED.mp4...")

            for idx, clip in enumerate(clips, 1):
                start = clip["start"]
                end = clip["end"]
                fname = re.sub(r"[^a-zA-Z0-9_-]", "_", clip["filename"])
                title = clip["title"].replace(":", "\\:").replace("'", "").replace("%", "%%")
                desc_meta = clip.get("desc", clip["title"])
                out_file = os.path.join(out_dir, f"{fname}.mp4")

                self.log_signal.emit(f"\n[>] Short {idx}/{len(clips)}: {clip['title']} ({start} -> {end})")

                video_fc = (
                    "[0:v]split=2[bg][fg];"
                    "[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,avgblur=30[bg_b];"
                    "[fg]scale=1080:-1[fg_s];"
                    "[bg_b][fg_s]overlay=(W-w)/2:(H-h)/2,"
                    f"drawtext=expansion=none:text='{title}':font='{font_name}\\:style=Bold':fontcolor=white:fontsize=38:bordercolor=black:borderw=4:shadowcolor=black@0.6:shadowx=2:shadowy=2:x=(w-text_w)/2:y=240,"
                    f"subtitles='{srt_rel}':force_style='PlayResX=1080,PlayResY=1920,FontSize=42,FontName={font_name},Bold=1,PrimaryColour=&H0000FFFF,OutlineColour=&H00000000,BackColour=&H80000000,BorderStyle=1,Outline=3,Shadow=2,Alignment=2,MarginV=180',"
                    "setpts=PTS-STARTPTS[v]"
                )

                cmd_short = [
                    "ffmpeg", "-y",
                    "-ss", start, "-to", end, "-copyts", "-i", video_clean,
                    "-filter_complex", video_fc,
                    "-map", "[v]", "-map", "0:a:0",
                    "-af", "asetpts=PTS-STARTPTS",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                    "-c:a", "aac", "-b:a", "192k",
                    "-metadata", f"title={clip['title']}",
                    "-metadata", f"description={desc_meta}",
                    "-metadata", "artist=Julio Cesar",
                    "-metadata", "genre=Technology / Linux Tutorial",
                    out_file
                ]
                self.run_cmd(cmd_short, cwd=work_dir)
                pct = 76 + int((idx / max(len(clips), 1)) * 24)
                self.progress_signal.emit(pct)

            self.progress_signal.emit(100)
            resumen = (
                f"Done ({target_lang_name}):\n"
                f"  • Full Horizontal: {video_clean}\n"
                f"  • Full Vertical:   {video_vertical if self.cfg['gen_full_vertical'] else 'Skipped'}\n"
                f"  • Shorts created:  {len(clips)} in {out_dir}"
            )
            self.finished_signal.emit(resumen)
        except Exception as exc:
            self.error_signal.emit(str(exc))


# =====================================================================
# INTERFAZ PRINCIPAL CYBERPUNK MULTILENGUAJE
# =====================================================================

class CyberShortsStudio(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui_lang = "es"
        self.status_key = "status_standby"
        self.last_levels = None
        self.resize(1320, 910)
        self.preview_toggle = 0
        self.preview_worker = None
        self.pipeline_worker = None
        self.tts_test_worker = None
        self.tts_voices = []
        self.presets_data = self._load_presets_disk()

        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.audio_output.setVolume(1.0)
        self.player.setAudioOutput(self.audio_output)

        self._build_ui()
        self.setStyleSheet(CYBERPUNK_QSS)
        self._refresh_presets_combo()
        self._refresh_tts_voices()
        self._restore_last_state()
        self._retranslate_ui()

    def _tr(self, key):
        return TRANSLATIONS.get(self.ui_lang, TRANSLATIONS["es"]).get(
            key, TRANSLATIONS["es"].get(key, key)
        )

    def _load_presets_disk(self):
        data = {"presets": dict(BUILTIN_PRESETS), "last_state": None}
        if os.path.exists(PRESETS_FILE):
            try:
                with open(PRESETS_FILE, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                if isinstance(loaded, dict):
                    merged = dict(BUILTIN_PRESETS)
                    merged.update(loaded.get("presets", {}))
                    data["presets"] = merged
                    data["last_state"] = loaded.get("last_state")
            except Exception:
                pass
        return data

    def _write_presets_disk(self):
        try:
            with open(PRESETS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.presets_data, f, indent=2, ensure_ascii=False)
        except Exception as exc:
            self._log(f"[!] Could not save {PRESETS_FILE}: {exc}")

    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        main_layout = QVBoxLayout(root)
        main_layout.setContentsMargins(12, 10, 12, 10)
        main_layout.setSpacing(8)

        # Header HUD + Selector de idioma UI
        header = QHBoxLayout()
        self.lbl_header_title = QLabel()
        self.lbl_header_title.setObjectName("HeaderTitle")

        self.lbl_ui_lang = QLabel()
        self.combo_ui_lang = QComboBox()
        for code, meta in LANG_META.items():
            self.combo_ui_lang.addItem(f"{meta['name']} ({code.upper()})", code)
        self.combo_ui_lang.currentIndexChanged.connect(self._on_ui_lang_changed)

        self.status_badge = QLabel()
        self.status_badge.setStyleSheet("color: #fcee0a; font-weight: bold;")

        header.addWidget(self.lbl_header_title)
        header.addStretch()
        header.addWidget(self.lbl_ui_lang)
        header.addWidget(self.combo_ui_lang)
        header.addSpacing(12)
        header.addWidget(self.status_badge)
        main_layout.addLayout(header)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter, 1)

        # --- PANEL IZQUIERDO ---
        left_frame = QFrame()
        left_frame.setObjectName("HudPanel")
        left_outer = QVBoxLayout(left_frame)
        left_outer.setContentsMargins(4, 4, 4, 4)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        left_content = QWidget()
        left_content.setStyleSheet("background-color: #0d111c;")
        left_layout = QVBoxLayout(left_content)
        left_layout.setSpacing(6)
        scroll.setWidget(left_content)
        left_outer.addWidget(scroll)

        # 01 Archivos
        self.lbl_sec_01 = QLabel()
        self.lbl_sec_01.setObjectName("SectionTitle")
        left_layout.addWidget(self.lbl_sec_01)

        self.drop_video1 = DropZone("", "", [".mp4", ".mkv", ".mov", ".webm"])
        self.drop_video2 = DropZone("", "", [".mp4", ".mkv", ".mov", ".webm"])
        self.drop_music = DropZone("", "", [".mp3", ".wav", ".ogg", ".flac", ".m4a"])

        left_layout.addWidget(self.drop_video1)
        left_layout.addWidget(self.drop_video2)

        music_row = QHBoxLayout()
        music_row.addWidget(self.drop_music, 1)
        self.btn_clear_music = QPushButton("✕")
        self.btn_clear_music.setFixedWidth(32)
        self.btn_clear_music.clicked.connect(self.drop_music.clear_file)
        music_row.addWidget(self.btn_clear_music)
        left_layout.addLayout(music_row)

        track_row = QHBoxLayout()
        self.lbl_mic_track = QLabel()
        track_row.addWidget(self.lbl_mic_track)
        self.combo_track = QComboBox()
        self.combo_track.addItem("", "auto")
        for i in range(4):
            self.combo_track.addItem("", str(i))
        track_row.addWidget(self.combo_track, 1)
        left_layout.addLayout(track_row)

        # 02 Presets
        self.lbl_sec_02 = QLabel()
        self.lbl_sec_02.setObjectName("SectionTitle")
        left_layout.addWidget(self.lbl_sec_02)

        preset_row = QHBoxLayout()
        self.combo_presets = QComboBox()
        self.btn_load_p = QPushButton()
        self.btn_load_p.clicked.connect(self._load_selected_preset)
        self.btn_save_p = QPushButton()
        self.btn_save_p.clicked.connect(self._save_new_preset)
        self.btn_del_p = QPushButton("✕")
        self.btn_del_p.setFixedWidth(30)
        self.btn_del_p.clicked.connect(self._delete_selected_preset)
        preset_row.addWidget(self.combo_presets, 1)
        preset_row.addWidget(self.btn_load_p)
        preset_row.addWidget(self.btn_save_p)
        preset_row.addWidget(self.btn_del_p)
        left_layout.addLayout(preset_row)

        # 03 Ecualizador 5 bandas (±48 dB)
        self.lbl_sec_03 = QLabel()
        self.lbl_sec_03.setObjectName("SectionTitle")
        left_layout.addWidget(self.lbl_sec_03)

        eq_frame = QFrame()
        eq_frame.setObjectName("EqBox")
        eq_layout = QHBoxLayout(eq_frame)
        eq_layout.setContentsMargins(6, 6, 6, 6)
        eq_layout.setSpacing(6)

        self.sliders = {}
        self.eq_name_labels = {}
        self.eq_freqs = {
            "eq_low": "110Hz",
            "eq_lowmid": "322Hz",
            "eq_mid": "837Hz",
            "eq_pres": "4.8kHz",
            "eq_high": "10kHz",
        }
        eq_defaults = [
            ("eq_low", 55), ("eq_lowmid", -40), ("eq_mid", -20), ("eq_pres", 45), ("eq_high", 35),
        ]

        for key, default in eq_defaults:
            col = QVBoxLayout()
            col.setAlignment(Qt.AlignmentFlag.AlignHCenter)

            val_lbl = QLabel(f"{default * 0.1:+.1f}dB")
            val_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            val_lbl.setStyleSheet("color: #fcee0a; font-size: 11px; font-weight: bold;")

            sl = QSlider(Qt.Orientation.Vertical)
            sl.setRange(-480, 480)
            sl.setValue(default)
            sl.setMinimumHeight(88)
            sl.valueChanged.connect(lambda v, l=val_lbl: l.setText(f"{v * 0.1:+.1f}dB"))

            name_lbl = QLabel()
            name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            name_lbl.setStyleSheet("color: #00f3ff; font-size: 10px; font-weight: bold;")
            self.eq_name_labels[key] = name_lbl

            col.addWidget(val_lbl)
            col.addWidget(sl, 0, Qt.AlignmentFlag.AlignHCenter)
            col.addWidget(name_lbl)
            eq_layout.addLayout(col)
            self.sliders[key] = (sl, 0.1)

        left_layout.addWidget(eq_frame)

        # 04 Efectos Pro
        self.lbl_sec_04 = QLabel()
        self.lbl_sec_04.setObjectName("SectionTitle")
        left_layout.addWidget(self.lbl_sec_04)

        fx_grid = QGridLayout()
        fx_grid.setSpacing(4)
        self.chk_deesser = QCheckBox()
        self.chk_exciter = QCheckBox()
        self.chk_warmth = QCheckBox()
        self.chk_dual_mono = QCheckBox()
        for cb in (self.chk_deesser, self.chk_exciter, self.chk_warmth, self.chk_dual_mono):
            cb.setChecked(True)
        fx_grid.addWidget(self.chk_deesser, 0, 0)
        fx_grid.addWidget(self.chk_exciter, 0, 1)
        fx_grid.addWidget(self.chk_warmth, 1, 0)
        fx_grid.addWidget(self.chk_dual_mono, 1, 1)
        left_layout.addLayout(fx_grid)

        # 05 Dinámica y Música
        self.lbl_sec_05 = QLabel()
        self.lbl_sec_05.setObjectName("SectionTitle")
        left_layout.addWidget(self.lbl_sec_05)

        grid = QGridLayout()
        grid.setSpacing(4)
        self.dyn_labels = {}
        dyn_defs = [
            ("voice_gain", "lbl_voice_gain", -120, 360, 85, 0.1, "{:+.1f} dB"),
            ("comp_ratio", "lbl_comp_ratio", 15, 80, 40, 0.1, "{:.1f}:1"),
            ("gate", "lbl_gate", 5, 80, 12, 0.001, "{:.3f}"),
            ("music_db", "lbl_music_db", -600, 120, -220, 0.1, "{:+.1f} dB"),
        ]

        for row, (key, tr_key, mn, mx, default, scale, fmt) in enumerate(dyn_defs):
            lbl = QLabel()
            self.dyn_labels[tr_key] = lbl
            sl = QSlider(Qt.Orientation.Horizontal)
            sl.setRange(mn, mx)
            sl.setValue(default)
            val_lbl = QLabel(fmt.format(default * scale))
            val_lbl.setFixedWidth(74)
            val_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            val_lbl.setStyleSheet("color: #fcee0a; font-weight: bold;")

            sl.valueChanged.connect(lambda v, l=val_lbl, s=scale, f=fmt: l.setText(f.format(v * s)))
            grid.addWidget(lbl, row, 0)
            grid.addWidget(sl, row, 1)
            grid.addWidget(val_lbl, row, 2)
            self.sliders[key] = (sl, scale)

        left_layout.addLayout(grid)

        self.chk_ducking = QCheckBox()
        self.chk_ducking.setChecked(True)
        left_layout.addWidget(self.chk_ducking)

        # 06 Guión IA, Idiomas de Contenido, TTS y Sincronía Labial
        self.lbl_sec_06 = QLabel()
        self.lbl_sec_06.setObjectName("SectionTitle")
        left_layout.addWidget(self.lbl_sec_06)

        lang_grid = QGridLayout()
        lang_grid.setSpacing(4)
        self.lbl_src_lang = QLabel()
        self.combo_src_lang = QComboBox()
        self.combo_src_lang.addItem("", "auto")
        for code, meta in LANG_META.items():
            self.combo_src_lang.addItem(f"{meta['name']} ({code})", code)

        self.lbl_dst_lang = QLabel()
        self.combo_dst_lang = QComboBox()
        for code, meta in LANG_META.items():
            self.combo_dst_lang.addItem(f"{meta['name']} ({code})", code)

        lang_grid.addWidget(self.lbl_src_lang, 0, 0)
        lang_grid.addWidget(self.combo_src_lang, 0, 1)
        lang_grid.addWidget(self.lbl_dst_lang, 1, 0)
        lang_grid.addWidget(self.combo_dst_lang, 1, 1)
        left_layout.addLayout(lang_grid)

        self.chk_polish_dialogue = QCheckBox()
        self.chk_polish_dialogue.setChecked(True)
        left_layout.addWidget(self.chk_polish_dialogue)

        self.chk_use_tts = QCheckBox()
        self.chk_use_tts.setChecked(False)
        left_layout.addWidget(self.chk_use_tts)

        tts_row = QHBoxLayout()
        self.combo_tts = QComboBox()
        self.btn_tts_test = QPushButton()
        self.btn_tts_test.clicked.connect(self._test_tts_voice)
        self.btn_tts_scan = QPushButton("↻")
        self.btn_tts_scan.setFixedWidth(32)
        self.btn_tts_scan.clicked.connect(self._refresh_tts_voices)
        tts_row.addWidget(self.combo_tts, 1)
        tts_row.addWidget(self.btn_tts_test)
        tts_row.addWidget(self.btn_tts_scan)
        left_layout.addLayout(tts_row)

        self.chk_lipsync = QCheckBox()
        self.chk_lipsync.setChecked(True)
        left_layout.addWidget(self.chk_lipsync)

        self.chk_tts_rack = QCheckBox()
        self.chk_tts_rack.setChecked(False)
        left_layout.addWidget(self.chk_tts_rack)

        # 07 Salida, Formatos y Ollama
        self.lbl_sec_07 = QLabel()
        self.lbl_sec_07.setObjectName("SectionTitle")
        left_layout.addWidget(self.lbl_sec_07)

        self.chk_full_vertical = QCheckBox()
        self.chk_full_vertical.setChecked(True)
        left_layout.addWidget(self.chk_full_vertical)

        out_row = QHBoxLayout()
        self.txt_outdir = QLineEdit(DEFAULT_OUT_DIR)
        self.btn_dir = QPushButton()
        self.btn_dir.clicked.connect(self._browse_outdir)
        out_row.addWidget(self.txt_outdir, 1)
        out_row.addWidget(self.btn_dir)
        left_layout.addLayout(out_row)

        ia_row = QHBoxLayout()
        self.lbl_ollama = QLabel()
        ia_row.addWidget(self.lbl_ollama)
        self.txt_model = QLineEdit(DEFAULT_OLLAMA_MODEL)
        ia_row.addWidget(self.txt_model, 1)
        self.chk_force = QCheckBox()
        self.chk_force.setChecked(True)
        ia_row.addWidget(self.chk_force)
        left_layout.addLayout(ia_row)

        self.btn_run = QPushButton()
        self.btn_run.setObjectName("ActionRun")
        self.btn_run.clicked.connect(self._start_pipeline)
        left_layout.addWidget(self.btn_run)

        # --- PANEL DERECHO ---
        right_panel = QFrame()
        right_panel.setObjectName("HudPanel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(8)

        self.lbl_sec_08 = QLabel()
        self.lbl_sec_08.setObjectName("SectionTitle")
        right_layout.addWidget(self.lbl_sec_08)

        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumHeight(300)
        self.video_widget.setStyleSheet("background-color: #020306; border: 1px solid #00f3ff;")
        self.player.setVideoOutput(self.video_widget)
        right_layout.addWidget(self.video_widget, 3)

        prev_ctrl = QHBoxLayout()
        self.lbl_prev_start = QLabel()
        prev_ctrl.addWidget(self.lbl_prev_start)
        self.spin_start = QSpinBox()
        self.spin_start.setRange(0, 7200)
        self.spin_start.setValue(35)
        prev_ctrl.addWidget(self.spin_start)

        self.btn_preview = QPushButton()
        self.btn_preview.setObjectName("ActionPreview")
        self.btn_preview.clicked.connect(self._generate_preview)
        prev_ctrl.addWidget(self.btn_preview, 1)

        self.btn_play = QPushButton()
        self.btn_play.clicked.connect(self._toggle_play)
        prev_ctrl.addWidget(self.btn_play)
        right_layout.addLayout(prev_ctrl)

        self.seek_slider = QSlider(Qt.Orientation.Horizontal)
        self.seek_slider.sliderMoved.connect(self.player.setPosition)
        self.player.positionChanged.connect(self.seek_slider.setValue)
        self.player.durationChanged.connect(lambda d: self.seek_slider.setRange(0, d))
        right_layout.addWidget(self.seek_slider)

        self.lbl_levels = QLabel()
        self.lbl_levels.setStyleSheet("color: #00f3ff; font-weight: bold;")
        right_layout.addWidget(self.lbl_levels)

        self.vu_bar = QProgressBar()
        self.vu_bar.setRange(0, 100)
        self.vu_bar.setValue(0)
        right_layout.addWidget(self.vu_bar)

        self.lbl_sec_09 = QLabel()
        self.lbl_sec_09.setObjectName("SectionTitle")
        right_layout.addWidget(self.lbl_sec_09)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        right_layout.addWidget(self.log_box, 2)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        right_layout.addWidget(self.progress_bar)

        splitter.addWidget(left_frame)
        splitter.addWidget(right_panel)
        splitter.setSizes([580, 740])

    # --- CAMBIO DE IDIOMA EN VIVO ---
    def _on_ui_lang_changed(self):
        code = self.combo_ui_lang.currentData()
        if code and code in TRANSLATIONS:
            self.ui_lang = code
            self._retranslate_ui()
            self._save_last_state()

    def _set_status(self, status_key):
        self.status_key = status_key
        self.status_badge.setText(self._tr(status_key))

    def _retranslate_ui(self):
        direction = Qt.LayoutDirection.RightToLeft if self.ui_lang == "ar" else Qt.LayoutDirection.LeftToRight
        self.setLayoutDirection(direction)

        self.setWindowTitle(self._tr("win_title"))
        self.lbl_header_title.setText(self._tr("header_title"))
        self.lbl_ui_lang.setText(self._tr("ui_lang_lbl"))
        self.status_badge.setText(self._tr(self.status_key))

        self.lbl_sec_01.setText(self._tr("sec_01"))
        self.drop_video1.set_texts(self._tr("drop_v1"), self._tr("drop_hint"), self._tr("files_filter"))
        self.drop_video2.set_texts(self._tr("drop_v2"), self._tr("drop_hint"), self._tr("files_filter"))
        self.drop_music.set_texts(self._tr("drop_music"), self._tr("drop_hint"), self._tr("files_filter"))
        self.btn_clear_music.setToolTip(self._tr("tip_clear_music"))

        self.lbl_mic_track.setText(self._tr("mic_track"))
        self.combo_track.setItemText(0, self._tr("track_auto"))
        for i in range(4):
            self.combo_track.setItemText(i + 1, self._tr("track_n").format(n=i + 1, i=i))

        self.lbl_sec_02.setText(self._tr("sec_02"))
        self.btn_load_p.setText(self._tr("btn_load"))
        self.btn_save_p.setText(self._tr("btn_save"))
        self.btn_del_p.setToolTip(self._tr("tip_del_preset"))

        self.lbl_sec_03.setText(self._tr("sec_03"))
        for key, lbl in self.eq_name_labels.items():
            lbl.setText(f"{self._tr(key)}\n{self.eq_freqs[key]}")

        self.lbl_sec_04.setText(self._tr("sec_04"))
        self.chk_deesser.setText(self._tr("fx_deesser"))
        self.chk_exciter.setText(self._tr("fx_exciter"))
        self.chk_warmth.setText(self._tr("fx_warmth"))
        self.chk_dual_mono.setText(self._tr("fx_dual_mono"))

        self.lbl_sec_05.setText(self._tr("sec_05"))
        for tr_key, lbl in self.dyn_labels.items():
            lbl.setText(self._tr(tr_key))
        self.chk_ducking.setText(self._tr("chk_ducking"))

        self.lbl_sec_06.setText(self._tr("sec_06"))
        self.lbl_src_lang.setText(self._tr("lbl_src_lang"))
        self.lbl_dst_lang.setText(self._tr("lbl_dst_lang"))
        self.combo_src_lang.setItemText(0, self._tr("lang_auto"))
        self.chk_polish_dialogue.setText(self._tr("chk_polish"))
        self.chk_use_tts.setText(self._tr("chk_use_tts"))
        self.btn_tts_test.setText(self._tr("btn_tts_test"))
        self.btn_tts_scan.setToolTip(self._tr("tip_tts_scan"))
        if not self.tts_voices and self.combo_tts.count() > 0:
            self.combo_tts.setItemText(0, self._tr("no_tts"))
        self.chk_lipsync.setText(self._tr("chk_lipsync"))
        self.chk_tts_rack.setText(self._tr("chk_tts_rack"))

        self.lbl_sec_07.setText(self._tr("sec_07"))
        self.chk_full_vertical.setText(self._tr("chk_full_vert"))
        self.btn_dir.setText(self._tr("btn_dir"))
        self.lbl_ollama.setText(self._tr("lbl_ollama"))
        self.chk_force.setText(self._tr("chk_force"))
        self.btn_run.setText(self._tr("btn_run"))

        self.lbl_sec_08.setText(self._tr("sec_08"))
        self.lbl_prev_start.setText(self._tr("lbl_prev_start"))
        self.btn_preview.setText(self._tr("btn_preview"))
        self.btn_play.setText(self._tr("btn_play"))
        self.lbl_sec_09.setText(self._tr("sec_09"))

        if self.last_levels is None:
            self.lbl_levels.setText(self._tr("meter_idle"))
            self.vu_bar.setFormat(self._tr("vu_idle"))
        else:
            self._update_level_display(*self.last_levels)

    # --- VOCES TTS ---
    def _refresh_tts_voices(self):
        prev_id = self.combo_tts.currentData()["id"] if self.combo_tts.currentData() else None
        self.tts_voices = discover_tts_voices()
        self.combo_tts.clear()
        if not self.tts_voices:
            self.combo_tts.addItem(self._tr("no_tts"), None)
        else:
            for v in self.tts_voices:
                self.combo_tts.addItem(v["label"], v)
            if prev_id:
                for i in range(self.combo_tts.count()):
                    data = self.combo_tts.itemData(i)
                    if data and data["id"] == prev_id:
                        self.combo_tts.setCurrentIndex(i)
                        break
        clones = sum(1 for v in self.tts_voices if v["engine"] == "f5_daemon")
        self._log(f"[*] TTS voices detected: {len(self.tts_voices)} ({clones} cloned RAM socket)")

    def _test_tts_voice(self):
        voice = self.combo_tts.currentData()
        if not voice:
            self._log(self._tr("err_no_tts"))
            return
        self.player.stop()
        self.player.setSource(QUrl())
        self.btn_tts_test.setEnabled(False)
        self._set_status("status_tts_run")
        self.preview_toggle = 1 - self.preview_toggle
        out_wav = os.path.join(tempfile.gettempdir(), f"cyber_tts_test_{self.preview_toggle}.wav")
        lang = self.combo_dst_lang.currentData() or "es"

        self.tts_test_worker = TtsTestWorker(voice, out_wav, lang)
        self.tts_test_worker.log_signal.connect(self._log)
        self.tts_test_worker.finished_signal.connect(self._on_tts_test_ready)
        self.tts_test_worker.error_signal.connect(self._on_tts_test_error)
        self.tts_test_worker.start()

    def _on_tts_test_ready(self, wav_path):
        self.btn_tts_test.setEnabled(True)
        self._set_status("status_tts_ok")
        self._log(f"[✓] Playing TTS test: {os.path.basename(wav_path)}")
        self.player.setSource(QUrl.fromLocalFile(wav_path))
        self.player.play()

    def _on_tts_test_error(self, err):
        self.btn_tts_test.setEnabled(True)
        self._set_status("status_tts_err")
        self._log(f"[X] TTS test error:\n{err}")

    # --- PRESETS PERSISTENTES ---
    def _capture_preset_dict(self):
        state = {key: sl.value() for key, (sl, _) in self.sliders.items()}
        tts_data = self.combo_tts.currentData()
        state.update({
            "ui_lang": self.ui_lang,
            "source_lang": self.combo_src_lang.currentData() or "auto",
            "target_lang": self.combo_dst_lang.currentData() or "es",
            "ducking": self.chk_ducking.isChecked(),
            "fx_deesser": self.chk_deesser.isChecked(),
            "fx_exciter": self.chk_exciter.isChecked(),
            "fx_warmth": self.chk_warmth.isChecked(),
            "fx_dual_mono": self.chk_dual_mono.isChecked(),
            "out_dir": self.txt_outdir.text().strip(),
            "ollama_model": self.txt_model.text().strip(),
            "track_index": self.combo_track.currentIndex(),
            "polish_dialogue": self.chk_polish_dialogue.isChecked(),
            "use_tts": self.chk_use_tts.isChecked(),
            "tts_voice_id": tts_data["id"] if tts_data else "",
            "lipsync_strict": self.chk_lipsync.isChecked(),
            "tts_apply_rack": self.chk_tts_rack.isChecked(),
            "gen_full_vertical": self.chk_full_vertical.isChecked(),
        })
        return state

    def _select_combo_by_data(self, combo, value):
        for i in range(combo.count()):
            if combo.itemData(i) == value:
                combo.blockSignals(True)
                combo.setCurrentIndex(i)
                combo.blockSignals(False)
                return True
        return False

    def _apply_preset_dict(self, state):
        if not isinstance(state, dict):
            return
        if state.get("ui_lang") in TRANSLATIONS:
            self.ui_lang = state["ui_lang"]
            self._select_combo_by_data(self.combo_ui_lang, self.ui_lang)
        if state.get("source_lang"):
            self._select_combo_by_data(self.combo_src_lang, state["source_lang"])
        if state.get("target_lang"):
            self._select_combo_by_data(self.combo_dst_lang, state["target_lang"])

        for key, (sl, _) in self.sliders.items():
            if key in state:
                sl.setValue(int(state[key]))
        for attr, key in (
            (self.chk_ducking, "ducking"),
            (self.chk_deesser, "fx_deesser"),
            (self.chk_exciter, "fx_exciter"),
            (self.chk_warmth, "fx_warmth"),
            (self.chk_dual_mono, "fx_dual_mono"),
            (self.chk_polish_dialogue, "polish_dialogue"),
            (self.chk_use_tts, "use_tts"),
            (self.chk_lipsync, "lipsync_strict"),
            (self.chk_tts_rack, "tts_apply_rack"),
            (self.chk_full_vertical, "gen_full_vertical"),
        ):
            if key in state:
                attr.setChecked(bool(state[key]))
        if state.get("out_dir"):
            self.txt_outdir.setText(state["out_dir"])
        if state.get("ollama_model"):
            self.txt_model.setText(state["ollama_model"])
        if "track_index" in state:
            self.combo_track.setCurrentIndex(int(state["track_index"]))
        if state.get("tts_voice_id"):
            for i in range(self.combo_tts.count()):
                data = self.combo_tts.itemData(i)
                if data and data["id"] == state["tts_voice_id"]:
                    self.combo_tts.setCurrentIndex(i)
                    break

    def _refresh_presets_combo(self, select_name=None):
        self.combo_presets.clear()
        for name in self.presets_data["presets"]:
            self.combo_presets.addItem(name)
        if select_name:
            idx = self.combo_presets.findText(select_name)
            if idx >= 0:
                self.combo_presets.setCurrentIndex(idx)

    def _restore_last_state(self):
        last = self.presets_data.get("last_state")
        if last:
            self._apply_preset_dict(last)
            self._log("[*] Last session settings restored.")

    def _save_last_state(self):
        self.presets_data["last_state"] = self._capture_preset_dict()
        self._write_presets_disk()

    def _load_selected_preset(self):
        name = self.combo_presets.currentText()
        preset = self.presets_data["presets"].get(name)
        if preset:
            self._apply_preset_dict(preset)
            self._retranslate_ui()
            self._save_last_state()
            self._log(f"[*] Preset loaded: {name}")

    def _save_new_preset(self):
        current_name = self.combo_presets.currentText()
        name, ok = QInputDialog.getText(
            self, self._tr("dlg_save_title"), self._tr("dlg_save_prompt"), text=current_name
        )
        name = name.strip()
        if ok and name:
            self.presets_data["presets"][name] = self._capture_preset_dict()
            self._save_last_state()
            self._refresh_presets_combo(select_name=name)
            self._log(f"[✓] Preset saved: {name}")

    def _delete_selected_preset(self):
        name = self.combo_presets.currentText()
        if name in BUILTIN_PRESETS:
            self._log(f"[!] '{name}' is a built-in preset and cannot be deleted.")
            return
        if name in self.presets_data["presets"]:
            del self.presets_data["presets"][name]
            self._write_presets_disk()
            self._refresh_presets_combo()
            self._log(f"[*] Preset deleted: {name}")

    def closeEvent(self, event):
        self._save_last_state()
        self.player.stop()
        super().closeEvent(event)

    # --- CONTROL GENERAL ---
    def _get_cfg(self):
        cfg = {key: sl.value() * scale for key, (sl, scale) in self.sliders.items()}
        cfg.update({
            "source_lang": self.combo_src_lang.currentData() or "auto",
            "target_lang": self.combo_dst_lang.currentData() or "es",
            "ducking": self.chk_ducking.isChecked(),
            "fx_deesser": self.chk_deesser.isChecked(),
            "fx_exciter": self.chk_exciter.isChecked(),
            "fx_warmth": self.chk_warmth.isChecked(),
            "fx_dual_mono": self.chk_dual_mono.isChecked(),
            "track": self.combo_track.currentData(),
            "preview_start": self.spin_start.value(),
            "out_dir": self.txt_outdir.text().strip() or DEFAULT_OUT_DIR,
            "ollama_model": self.txt_model.text().strip() or DEFAULT_OLLAMA_MODEL,
            "force_reprocess": self.chk_force.isChecked(),
            "polish_dialogue": self.chk_polish_dialogue.isChecked(),
            "use_tts": self.chk_use_tts.isChecked(),
            "lipsync_strict": self.chk_lipsync.isChecked(),
            "tts_apply_rack": self.chk_tts_rack.isChecked(),
            "gen_full_vertical": self.chk_full_vertical.isChecked(),
        })
        return cfg

    def _browse_outdir(self):
        d = QFileDialog.getExistingDirectory(self, self._tr("dlg_outdir"), self.txt_outdir.text())
        if d:
            self.txt_outdir.setText(d)

    def _log(self, text):
        self.log_box.append(text)
        sb = self.log_box.verticalScrollBar()
        sb.setValue(sb.maximum())

    def _toggle_play(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    def _update_level_display(self, mean_db, max_db):
        pct = max(0, min(100, int(((mean_db + 45.0) / 40.0) * 100)))
        self.vu_bar.setValue(pct)
        self.vu_bar.setFormat(self._tr("vu_fmt").format(mean=mean_db, max=max_db))

        if -16.0 <= mean_db <= -10.5:
            color, key = "#00ff9c", "lvl_ok"
        elif mean_db < -16.0:
            color, key = "#fcee0a", "lvl_low"
        else:
            color, key = "#ff0055", "lvl_high"

        self.vu_bar.setStyleSheet(f"QProgressBar::chunk {{ background-color: {color}; }}")
        self.lbl_levels.setText(self._tr(key))
        self.lbl_levels.setStyleSheet(f"color: {color}; font-weight: bold;")

    def _generate_preview(self):
        if not self.drop_video1.file_path:
            self._log(self._tr("err_no_video"))
            return

        self._save_last_state()
        self.player.stop()
        self.player.setSource(QUrl())
        self.btn_preview.setEnabled(False)
        self._set_status("status_preview_run")

        self.preview_toggle = 1 - self.preview_toggle
        out_tmp = os.path.join(tempfile.gettempdir(), f"cyber_preview_{self.preview_toggle}.mp4")

        self.preview_worker = PreviewWorker(
            self.drop_video1.file_path,
            self.drop_music.file_path,
            self._get_cfg(),
            out_tmp,
        )
        self.preview_worker.log_signal.connect(self._log)
        self.preview_worker.finished_signal.connect(self._on_preview_ready)
        self.preview_worker.error_signal.connect(self._on_preview_error)
        self.preview_worker.start()

    def _on_preview_ready(self, path, mean_db, max_db):
        self.btn_preview.setEnabled(True)
        self._set_status("status_preview_ok")
        self.last_levels = (mean_db, max_db)
        self._log(f"[✓] Preview ready | Mean: {mean_db:.1f} dB | Peak: {max_db:.1f} dB")
        self._update_level_display(mean_db, max_db)
        self.player.setSource(QUrl.fromLocalFile(path))
        self.player.play()

    def _on_preview_error(self, err):
        self.btn_preview.setEnabled(True)
        self._set_status("status_preview_err")
        self._log(f"[X] Preview error:\n{err}")

    def _start_pipeline(self):
        if not self.drop_video1.file_path:
            self._log(self._tr("err_no_video"))
            return

        self._save_last_state()
        self.player.stop()
        self.btn_run.setEnabled(False)
        self.btn_preview.setEnabled(False)
        self.btn_tts_test.setEnabled(False)
        self.progress_bar.setValue(0)
        self._set_status("status_pipe_run")

        self.pipeline_worker = PipelineWorker(
            self.drop_video1.file_path,
            self.drop_video2.file_path,
            self.drop_music.file_path,
            self._get_cfg(),
            self.combo_tts.currentData(),
        )
        self.pipeline_worker.log_signal.connect(self._log)
        self.pipeline_worker.progress_signal.connect(self.progress_bar.setValue)
        self.pipeline_worker.finished_signal.connect(self._on_pipeline_done)
        self.pipeline_worker.error_signal.connect(self._on_pipeline_error)
        self.pipeline_worker.start()

    def _on_pipeline_done(self, msg):
        self.btn_run.setEnabled(True)
        self.btn_preview.setEnabled(True)
        self.btn_tts_test.setEnabled(True)
        self._set_status("status_pipe_ok")
        self._log(f"\n[✓] {msg}")

    def _on_pipeline_error(self, err):
        self.btn_run.setEnabled(True)
        self.btn_preview.setEnabled(True)
        self.btn_tts_test.setEnabled(True)
        self._set_status("status_pipe_err")
        self._log(f"\n[X] Pipeline error:\n{err}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = CyberShortsStudio()
    win.show()
    sys.exit(app.exec())
