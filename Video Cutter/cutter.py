import sys
import os
import subprocess
import imageio_ffmpeg

def parse_time(timestr):
    parts = [int(p) for p in timestr.split(":")]
    if len(parts) == 3:
        h, m, s = parts
        return h * 3600 + m * 60 + s
    elif len(parts) == 2:
        m, s = parts
        return m * 60 + s
    elif len(parts) == 1:
        return parts[0]
    else:
        raise ValueError("Invalid time format")

def to_ffmpeg_time(seconds):
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02}:{m:02}:{s:02}"

def get_video_info(input_file, ffmpeg_path):
    import json
    import shutil
    # Recherche le chemin de ffprobe (dans le même dossier que ffmpeg)
    ffmpeg_dir = os.path.dirname(ffmpeg_path)
    ffprobe_path = os.path.join(ffmpeg_dir, "ffprobe.exe")
    if not os.path.isfile(ffprobe_path):
        # Fallback: chercher ffprobe dans le PATH système
        ffprobe_path = shutil.which("ffprobe")
        if not ffprobe_path:
            print("ffprobe introuvable. Vérifiez votre installation imageio-ffmpeg.")
            return None
    cmd = [
        ffprobe_path,
        "-v", "error",
        "-show_entries", "format=duration:stream=codec_type,codec_name,width,height,avg_frame_rate",
        "-of", "json",
        input_file
    ]
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        info = json.loads(output.decode("utf-8"))
        duration = float(info["format"]["duration"])
        streams = info.get("streams", [])
        video_stream = next((s for s in streams if s.get("codec_type") == "video"), {})
        audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), {})
        width = video_stream.get("width")
        height = video_stream.get("height")
        fps = None
        if "avg_frame_rate" in video_stream and video_stream["avg_frame_rate"] != "0/0":
            num, den = video_stream["avg_frame_rate"].split("/")
            fps = round(float(num) / float(den), 2) if float(den) != 0 else None
        vcodec = video_stream.get("codec_name")
        acodec = audio_stream.get("codec_name")
        return {
            "duration": duration,
            "width": width,
            "height": height,
            "fps": fps,
            "vcodec": vcodec,
            "acodec": acodec
        }
    except Exception as e:
        print("Impossible de récupérer les infos de la vidéo :", e)
        return None

if __name__ == "__main__":
    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()

    # Mode interactif si pas d'arguments
    if len(sys.argv) == 1:
        input_file = input("Chemin du fichier vidéo : ").strip()
        if not os.path.isfile(input_file):
            print("Fichier introuvable.")
            sys.exit(1)
        info = get_video_info(input_file, ffmpeg_path)
        if not info:
            sys.exit(1)
        print(f"Durée : {int(info['duration']//60)} min {int(info['duration']%60)} sec ({info['duration']:.2f} s)")
        print(f"Résolution : {info['width']}x{info['height']}")
        print(f"FPS : {info['fps']}")
        print(f"Codec vidéo : {info['vcodec']}")
        print(f"Codec audio : {info['acodec']}")
        print()
        # Nouvelle fonctionnalité : découpage automatique en intervalles
        choix = input("Voulez-vous découper la vidéo en intervalles réguliers ? (o/n) : ").strip().lower()
        if choix == "o":
            interval_str = input("Durée de chaque intervalle (en secondes, ex: 30) : ").strip()
            try:
                interval = int(interval_str)
                if interval <= 0:
                    raise ValueError()
            except Exception:
                print("Entrée invalide.")
                sys.exit(1)
            total = int(info['duration'] // interval)
            print(f"Nombre de segments possibles : {total}")
            for i in range(total):
                start = i * interval
                end = min((i + 1) * interval, int(info['duration']))
                print(f"Segment {i+1}: {to_ffmpeg_time(start)} - {to_ffmpeg_time(end)}")
            reste = int(info['duration']) % interval
            if reste > 0:
                print(f"Reste non inclus : {to_ffmpeg_time(total*interval)} - {to_ffmpeg_time(int(info['duration']))} ({reste} sec)")
            sys.exit(0)
        # ...existing code for interactive cut...
        start_time = parse_time(input("Temps de début (ex: 0:00:10) : ").strip())
        end_time = parse_time(input("Temps de fin (ex: 0:01:00) : ").strip())
    elif len(sys.argv) == 2:
        # Mode interactif si un seul argument (le fichier vidéo)
        input_file = sys.argv[1]
        if not os.path.isfile(input_file):
            print("Fichier introuvable.")
            sys.exit(1)
        info = get_video_info(input_file, ffmpeg_path)
        if not info:
            sys.exit(1)
        print(f"Durée : {int(info['duration']//60)} min {int(info['duration']%60)} sec ({info['duration']:.2f} s)")
        print(f"Résolution : {info['width']}x{info['height']}")
        print(f"FPS : {info['fps']}")
        print(f"Codec vidéo : {info['vcodec']}")
        print(f"Codec audio : {info['acodec']}")
        print()
        choix = input("Voulez-vous découper la vidéo en intervalles réguliers ? (o/n) : ").strip().lower()
        if choix == "o":
            interval_str = input("Durée de chaque intervalle (en secondes, ex: 30) : ").strip()
            try:
                interval = int(interval_str)
                if interval <= 0:
                    raise ValueError()
            except Exception:
                print("Entrée invalide.")
                sys.exit(1)
            total = int(info['duration'] // interval)
            print(f"Nombre de segments possibles : {total}")
            for i in range(total):
                start = i * interval
                end = min((i + 1) * interval, int(info['duration']))
                print(f"Segment {i+1}: {to_ffmpeg_time(start)} - {to_ffmpeg_time(end)}")
            reste = int(info['duration']) % interval
            if reste > 0:
                print(f"Reste non inclus : {to_ffmpeg_time(total*interval)} - {to_ffmpeg_time(int(info['duration']))} ({reste} sec)")
            sys.exit(0)
        start_time = parse_time(input("Temps de début (ex: 0:00:10) : ").strip())
        end_time = parse_time(input("Temps de fin (ex: 0:01:00) : ").strip())
    elif len(sys.argv) == 4:
        input_file = sys.argv[1]
        start_time = parse_time(sys.argv[2])
        end_time = parse_time(sys.argv[3])
    else:
        print("Usage: python cutter.py <input_video> <start_time> <end_time>")
        print("Ou lancez sans argument ou avec juste le fichier vidéo pour le mode interactif.")
        sys.exit(1)

    duration = end_time - start_time
    if duration <= 0:
        print("End time must be after start time.")
        sys.exit(1)

    output_file = f"cut_{os.path.basename(input_file)}"
    # Vérification de la durée réelle de la vidéo
    info = get_video_info(input_file, ffmpeg_path)
    if info is None:
        sys.exit(1)
    video_duration = info["duration"]
    if start_time >= video_duration:
        print(f"Start time ({start_time}s) is after video duration ({video_duration:.2f}s).")
        sys.exit(1)
    if end_time > video_duration:
        print(f"End time ({end_time}s) is after video duration ({video_duration:.2f}s).")
        sys.exit(1)

    start_str = to_ffmpeg_time(start_time)
    duration_str = to_ffmpeg_time(duration)

    cmd = [
        ffmpeg_path,
        "-y",
        "-ss", start_str,
        "-i", input_file,
        "-t", duration_str,
        "-c:v", "libx264",
        "-c:a", "aac",
        output_file
    ]
    print("Running command:", " ".join(f'"{c}"' if ' ' in c else c for c in cmd))
    ret = subprocess.call(cmd)
    if ret == 0:
        print(f"Saved cut video as {output_file}")
    else:
        print("Erreur lors de la découpe avec ffmpeg.")
