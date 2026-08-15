---
song: крила-складу-псалом-11
artifact: suno
variant: d
style: hillsong
---

# Крила складу (Псалом 11) — вариант d, генерация в Suno

Строки взяты из карточки [[styles/hillsong]] и дополнены защитой от вокализаций
по [[craft/suno]]. Ориентир — Hillsong, первый уровень [[styles/references]];
имя группы в промпт не вписано, Suno фильтрует имена исполнителей.

## Style

```
contemporary Christian pop-rock ballad, 4/4 at 72 BPM, anthemic chorus, male
lead with supporting group vocals singing the written lyrics only, atmospheric
electric guitar swells, wide reverb pads, steady build from a soft verse to a
full-band chorus and back down at the end, clean straight-tone vocal, syllabic
delivery (one note per syllable), restrained on-the-beat phrasing, no runs, no
ad-libs, every sung sound is a written word, no vocalizations, no vocal fills
between lines, silence where there are no lyrics, instrumental sections stay
fully instrumental with no voice at all, the song ends on the written last line
and stops
```

## Exclude Styles

```
melisma, vocal runs, vocal riffs, ad-libs, ooohs and aaahs, whoa-oh chants,
spontaneous worship, oversinging, vocal improvisation, vocalizations, vocalise,
scat singing, vocal fills, improvised vocal tail, outro vocalizing, yeah yeah,
hey hey, oh oh, ah ah, eh eh, crowd vocals, crowd noise, live audience,
audience shouts, wordless backing vocals, background vocalizations, chanting,
vocal pads, key change, gospel choir, EDM, trap drums, autotune, orchestral
strings, country, americana
```

## Советы по генерации

- **Провальный дубль — тот, где последний припев громче предыдущего.** По брифу
  финал должен звучать свободнее, а не мощнее: у псалма нет счастливой развязки,
  ст. 6 — огонь и сера. Если Suno выводит третий припев на стадионный пик,
  перегенерируй. `key change` стоит в Exclude ровно за этим — модуляция к финалу
  превращает суд в праздник.
- **`spontaneous worship` держи в Exclude целиком**, несмотря на жанр: карточка
  предупреждает, что этот стиль сам тянет за собой распевки.
- **Слушай хвост проигрыша.** `[Instrumental break]` помечен как безголосый, а
  текст заканчивается `[End]` — на прошлых дублях именно там появлялось «е-е».
- **Подпевка поёт слова.** `supporting group vocals singing the written lyrics
  only` в Style плюс антивыкриковый блок в Exclude: никаких «о-о-о» на фоне
  припева.
- **72 BPM** — медленнее всех остальных вариантов этой песни, кроме `b` (70).
  Разводить их надо не темпом, а фактурой: у `b` акустика и нарратив без
  припева, здесь пэды и большой хук.
- **Длина.** Десять секций, ожидаемо 3:20–3:40. Если режет — убрать второй
  `[Pre-Chorus]`, а не припев.
