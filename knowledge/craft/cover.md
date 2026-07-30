# Ремесло: обложка

Обложка генерируется картиночной моделью (nano banana / Gemini image) по
промпту, который лежит в песне как `cover-prompt.md`. Заголовок и описание
ролика — в [[craft/youtube]]; на самой картинке текста быть не должно.

## Базовый промпт

Заполни плейсхолдеры в `{ }` и вставь промпт целиком.

```
Generate a music cover artwork in 16:9 widescreen aspect ratio, 1920×1080 pixels.

Mood / theme: {настроение и тема песни — например "meditative ambient,
foggy pine forest at dawn, cold blue palette"}.
Visual style: {стиль — например "cinematic photographic", "hand-painted
illustration", "retro film grain"}.

Composition requirements:
- Keep the main subject centered.
- Leave generous safe margins: no important element within the outer ~8%
  of any edge (so the frame survives padding/cropping for video).
- No text, no watermarks, no logos, no borders.
- Even, balanced lighting; avoid extreme detail in the far corners.

Output a single full-bleed image at 16:9, 1920×1080.
```

## Заметки

- Если модель не держит точный размер — главное соблюсти 16:9 и безопасные
  отступы; пайплайн (`just build`) всё равно впишет картинку в 1920×1080 с
  чёрным padding, ничего не обрезая.
- Сгенерированную картинку положи в папку песни как `cover.jpg` / `.png` —
  либо просто отдай файл команде `just import <slug> <путь>`, она сама даст
  каноническое имя, а прошлую обложку уберёт в `raw/`.
- В корне папки песни должна лежать **ровно одна** картинка, иначе сборка
  откажется угадывать.
