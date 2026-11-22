"""
Piper TTS Integration for Personal Assistant
High-quality, local, offline neural Text-to-Speech
"""

import os
import subprocess
import tempfile
import re
import shutil
from pathlib import Path
from urllib.request import urlopen

# Piper TTS imports
try:
    from piper import PiperVoice
    PIPER_AVAILABLE = True
except ImportError:
    PIPER_AVAILABLE = False
    print("[Piper TTS] Warning: piper-tts not installed. Run: pip install piper-tts onnxruntime")

# Default voice model path (will be downloaded on first use)
DEFAULT_VOICE = "en_US-lessac-medium"
VOICE_DIR = Path(__file__).parent / "piper_voices"
VOICE_DIR.mkdir(exist_ok=True)

# Global voice cache
_voice_cache = {}

# URL format from piper's download_voices.py
URL_FORMAT = "https://huggingface.co/rhasspy/piper-voices/resolve/main/{lang_family}/{lang_code}/{voice_name}/{voice_quality}/{lang_code}-{voice_name}-{voice_quality}{extension}?download=true"
VOICE_PATTERN = re.compile(
    r"^(?P<lang_family>[^-]+)_(?P<lang_region>[^-]+)-(?P<voice_name>[^-]+)-(?P<voice_quality>.+)$"
)


def _parse_voice_name(voice_name: str) -> dict:
    """Parse voice name into components."""
    voice_match = VOICE_PATTERN.match(voice_name)
    if not voice_match:
        raise ValueError(
            f"Voice '{voice_name}' did not match pattern: <language>-<name>-<quality> like 'en_US-lessac-medium'"
        )
    return {
        "lang_family": voice_match.group("lang_family"),
        "lang_code": voice_match.group("lang_family") + "_" + voice_match.group("lang_region"),
        "voice_name": voice_match.group("voice_name"),
        "voice_quality": voice_match.group("voice_quality"),
    }


def get_voice_path(voice_name: str = DEFAULT_VOICE) -> Path:
    """Get path to voice model, downloading if necessary."""
    voice_code = f"{voice_name}"
    voice_path = VOICE_DIR / f"{voice_code}.onnx"
    config_path = VOICE_DIR / f"{voice_code}.onnx.json"
    
    if voice_path.exists() and config_path.exists():
        return voice_path
    
    # Download voice model
    print(f"[Piper TTS] Downloading voice model: {voice_name}...")
    try:
        parts = _parse_voice_name(voice_name)
        
        # Download .onnx model
        model_url = URL_FORMAT.format(extension=".onnx", **parts)
        print(f"[Piper TTS] Downloading model from: {model_url}")
        with urlopen(model_url) as response:
            with open(voice_path, "wb") as model_file:
                shutil.copyfileobj(response, model_file)
        
        # Download .onnx.json config
        config_url = URL_FORMAT.format(extension=".onnx.json", **parts)
        print(f"[Piper TTS] Downloading config from: {config_url}")
        with urlopen(config_url) as response:
            with open(config_path, "wb") as config_file:
                shutil.copyfileobj(response, config_file)
        
        print(f"[Piper TTS] Voice model downloaded to: {voice_path}")
        return voice_path
    except Exception as e:
        print(f"[Piper TTS] Error downloading voice: {e}")
        raise


def get_piper_voice(voice_name: str = DEFAULT_VOICE) -> "PiperVoice":
    """Get or create PiperVoice instance (cached)."""
    if not PIPER_AVAILABLE:
        raise RuntimeError("piper-tts not installed")
    
    if voice_name not in _voice_cache:
        voice_path = get_voice_path(voice_name)
        print(f"[Piper TTS] Loading voice: {voice_name}...")
        _voice_cache[voice_name] = PiperVoice.load(str(voice_path))
        print(f"[Piper TTS] Voice loaded successfully")
    
    return _voice_cache[voice_name]


def synthesize_to_file(text: str, output_path: str, voice_name: str = DEFAULT_VOICE, 
                       speaker_id: int = 0, length_scale: float = 1.0, 
                       noise_scale: float = 0.667, noise_w: float = 0.8) -> bool:
    """
    Synthesize text to audio file using Piper TTS.
    
    Args:
        text: Text to synthesize
        output_path: Output WAV file path
        voice_name: Voice model name (e.g., en_US-lessac-medium, en_US-amy-low)
        speaker_id: Speaker ID for multi-speaker voices
        length_scale: Speech speed (1.0 = normal, >1.0 = slower, <1.0 = faster)
        noise_scale: Noise scale for generation
        noise_w: Noise width
    
    Returns:
        True if successful, False otherwise
    """
    if not PIPER_AVAILABLE:
        print("[Piper TTS] Error: piper-tts not available")
        return False
    
    try:
        import wave
        from piper.config import SynthesisConfig
        
        voice = get_piper_voice(voice_name)
        
        # Create synthesis config
        syn_config = SynthesisConfig(
            speaker_id=speaker_id if speaker_id > 0 else None,
            length_scale=length_scale,
            noise_scale=noise_scale,
            noise_w_scale=noise_w,
            normalize_audio=True,
            volume=1.0
        )
        
        # Synthesize to WAV file
        with wave.open(output_path, "wb") as wav_file:
            voice.synthesize_wav(text, wav_file, syn_config=syn_config)
        
        print(f"[Piper TTS] Audio saved to: {output_path}")
        return True
        
    except Exception as e:
        print(f"[Piper TTS] Synthesis error: {e}")
        import traceback
        traceback.print_exc()
        return False


def synthesize_and_play(text: str, voice_name: str = DEFAULT_VOICE, 
                        speaker_id: int = 0, length_scale: float = 1.0,
                        use_temp_file: bool = True) -> bool:
    """
    Synthesize text and play immediately.
    
    Args:
        text: Text to speak
        voice_name: Voice model name
        speaker_id: Speaker ID
        length_scale: Speech speed
        use_temp_file: Use temporary file (cleaned up after playback)
    
    Returns:
        True if successful
    """
    if use_temp_file:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            temp_path = tmp.name
    else:
        temp_path = "piper_output.wav"
    
    try:
        success = synthesize_to_file(text, temp_path, voice_name, speaker_id, length_scale)
        if not success:
            return False
        
        # Play audio using system player (blocking)
        result = play_audio_file(temp_path)
        return result
        
    finally:
        if use_temp_file and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass


def play_audio_file(file_path: str) -> bool:
    """Play audio file using available system player."""
    players = [
        ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet"],
        ["aplay"],
        ["paplay"],
        ["cvlc", "--play-and-exit"],
        ["mpv", "--no-video", "--really-quiet"],
    ]
    
    for player_cmd in players:
        try:
            # Don't capture output - let ffplay use the console for audio
            result = subprocess.run(player_cmd + [file_path], 
                                  timeout=30)
            if result.returncode == 0:
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
        except Exception as e:
            print(f"[Piper TTS] Player {player_cmd[0]} error: {e}")
            continue
    
    print(f"[Piper TTS] No working audio player found. Tried: {[p[0] for p in players]}")
    return False


def list_available_voices() -> list:
    """List recommended Piper voices for English."""
    return [
        "en_US-lessac-medium",    # Default, good quality
        "en_US-lessac-low",       # Lower quality, smaller
        "en_US-lessac-high",      # Higher quality, larger
        "en_US-amy-low",          # Female voice
        "en_US-amy-medium",       # Female voice
        "en_US-amy-high",         # Female voice
        "en_US-kathleen-low",     # Female voice
        "en_US-joe-medium",       # Male voice
        "en_GB-alba-medium",      # British female
        "en_GB-vctk-medium",      # British multi-speaker
    ]


def Main(inputVal: str, voice: str = DEFAULT_VOICE, play: bool = True) -> bool:
    """
    Main entry point for CLI integration.
    
    Args:
        inputVal: Text to speak
        voice: Voice model name
        play: Whether to play immediately (True) or just return success
    
    Returns:
        True if successful
    """
    print(f"[Piper TTS] Synthesizing: {inputVal[:80]}{'...' if len(inputVal) > 80 else ''}")
    
    if play:
        return synthesize_and_play(inputVal, voice_name=voice)
    else:
        output_path = "piper_output.wav"
        return synthesize_to_file(inputVal, output_path, voice_name=voice)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
        voice = DEFAULT_VOICE
        
        # Check for voice argument
        if "--voice" in sys.argv:
            idx = sys.argv.index("--voice")
            if idx + 1 < len(sys.argv):
                voice = sys.argv[idx + 1]
                text = " ".join([a for a in sys.argv[1:] if a != "--voice" and a != voice])
        
        Main(text, voice=voice)
    else:
        # Demo
        print("[Piper TTS] Demo mode")
        print(f"Available voices: {list_available_voices()}")
        Main("Hey SSB, this is your Personal Assistant with Piper TTS. All systems operational.")