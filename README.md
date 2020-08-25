# Color Detection Component
This component will take an image source and return the primary colors from that image.

```yaml
sensor:
  - platform: colordetection
    source: camera.front
    colors: 5
    quality: 5
```