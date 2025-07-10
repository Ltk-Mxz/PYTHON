# Video Cutter

Un script Python pour couper des vidéos facilement à l'aide de ffmpeg (via imageio-ffmpeg).

## **Dépendances**

- Python 3.7+
- [imageio-ffmpeg](https://pypi.org/project/imageio-ffmpeg/)

Installation des dépendances :

```bash
pip install imageio-ffmpeg
```

## Utilisation

### Mode interactif

Lancez simplement :

```bash
python cutter.py
```

Vous serez invité à entrer le chemin du fichier vidéo, puis le script affichera :

- La durée de la vidéo
- La résolution
- Le nombre de FPS
- Les codecs vidéo et audio

Vous pouvez ensuite :

- Découper la vidéo en intervalles réguliers (ex : segments de 30 secondes)
- Ou choisir un intervalle personnalisé (début et fin)

### Mode ligne de commande

Vous pouvez aussi lancer directement :

```bash
python cutter.py <fichier_video> <début> <fin>
```

Exemple :

```bash
python cutter.py holo.mp4 0:00:10 0:01:00
```

Les temps sont au format `h:m:s` ou `m:s` ou `s`.

### Exemple de découpage automatique

Si vous choisissez l'option "découper en intervalles réguliers", le script vous indiquera :

- Le nombre de segments possibles
- Les intervalles de chaque segment

**Note :**  
Le script vérifie automatiquement que les temps de découpe sont dans la durée réelle de la vidéo.

## Limitations

- Le script nécessite que `ffprobe.exe` soit accessible (fourni par imageio-ffmpeg ou installé dans le PATH).
- Le découpage ré-encode la vidéo en H.264/AAC pour garantir la compatibilité.

---
Auteur : Ltk Mxz
