# Air-Hockey-2D-Robotat-Edition

Este repositorio contiene la implementación completa del juego de Air Hockey desarrollado para el entorno **Robotat** de la Universidad del Valle de Guatemala, con soporte para control mediante marcadores, integración con **MQTT**, y un sistema gráfico basado en **pygame** y **pymunk**.

La estructura del repositorio incluye la versión final del juego, así como una versión previa sin lectura de marcadores para pruebas locales.

---

## Estructura del Proyecto

```
/juego_sin_markers
/assets
/src
```

---

## Subcarpeta: **juego_sin_markers**

Contiene el archivo:

- **main.py**  
  Corresponde a la **última versión del juego antes de integrar MQTT**.  
  Es útil para realizar pruebas **locales**, en una PC sin conexión al sistema de cámaras y red del laboratorio Robotat.

### Notas importantes
- Requiere modificar `players.py` para **desactivar la lectura de marcadores**.
- También es necesario deshabilitar la **asignación automática de posiciones** provenientes del sistema de captura de movimiento.

---

## Subcarpeta: **assets**

Contiene todos los **recursos gráficos** del juego:

- Sprites
- Fondos
- Elementos UI
- Iconos
- Fuente utilizada para textos del juego (incluyendo la pantalla de pausa)

Esta carpeta es cargada dinámicamente por el motor del juego.

---

## Subcarpeta: **src**

Es la subcarpeta principal del proyecto.  
Contiene la **versión final de todas las clases** del juego.

Todas están documentadas en el trabajo escrito del trabajo de graduación de Daniel Cortez de la Universidad del Valle de Guatemala, por si los comentarios del código no son suficientes.

### Clases incluidas:

- `game.py`
- `player.py`
- `goal.py`
- `puck.py`
- `ui_manager.py`
- `scoreboard.py`
- `main.py`
- `rink.py`

---

## game.py — Importaciones utilizadas

Este módulo es el núcleo del juego. Sus dependencias son:

```python
import pygame
import pymunk
import math
from scoreboard import Scoreboard
from rink import Rink
from puck import Puck
from player import Player
from goal import Goal
from ui_manager import UIManager, GameState
import json
import paho.mqtt.client as mqtt
import threading
import numpy as np
import cv2
```

---

## Requisitos

- Python 3.9+
- pygame
- pymunk  
- numpy
- opencv-python
- paho-mqtt
- json5
  
---

## Notas finales

- El código está optimizado para funcionar con el sistema de marcadores del laboratorio Robotat.
- La versión sin marcadores permite probar la jugabilidad sin depender de hardware externo.
- La versión final está preparada para integrarse con el pipeline de visión y control mediante MQTT.

---
