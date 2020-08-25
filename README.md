# Color Detection Component
This component will take an image source and return the primary colors from that image.

```yaml
sensor:
  - platform: colordetection
    source: media_player.shield
    color_count: 5
    quality: 3
  - platform: colordetection
    source: camera.front
    color_count: 2
    quality: 5
```