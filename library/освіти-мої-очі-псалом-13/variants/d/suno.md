---
song: освіти-мої-очі-псалом-13
artifact: suno
variant: d
style: hillsong
---

# Освіти мої очі (Псалом 13) — вариант d, генерация в Suno

Строки из карточки [[styles/hillsong]] плюс защита от вокализаций по
[[craft/suno]]. Ориентир — Hillsong, первый уровень [[styles/references]]; имя
группы в промпт не вписано, Suno фильтрует имена исполнителей.

## Style

```
contemporary Christian pop-rock ballad, 4/4 at 80 BPM, anthemic chorus, male
lead with supporting group vocals singing the written lyrics only, atmospheric
electric guitar swells, wide reverb pads, steady build across three choruses and
a complete drop to a single voice at the end, clean straight-tone vocal,
syllabic delivery (one note per syllable), restrained on-the-beat phrasing, no
runs, no ad-libs, every sung sound is a written word, no vocalizations, no vocal
fills between lines, silence where there are no lyrics, instrumental sections
stay fully instrumental with no voice at all, the song ends on the written last
line and stops
```

## Exclude Styles

```
melisma, vocal runs, vocal riffs, ad-libs, ooohs and aaahs, whoa-oh chants,
spontaneous worship, oversinging, vocal improvisation, vocalizations, vocalise,
scat singing, vocal fills, improvised vocal tail, outro vocalizing, yeah yeah,
hey hey, oh oh, ah ah, eh eh, crowd vocals, crowd noise, live audience, audience
shouts, wordless backing vocals, background vocalizations, chanting, vocal pads,
key change, final chorus lift, upbeat, cheerful, gospel choir, EDM, trap drums,
autotune, orchestral strings, country, americana
```

## Советы по генерации

- **Провальный дубль — бодрый.** Это жалоба, а не славословие; `upbeat` и
  `cheerful` стоят в Exclude намеренно. Если припев звучит радостно, вопрос
  «доки?» перестаёт быть вопросом.
- **Аутро — тише первого куплета, и поёт его один голос.** Обратный анфему ход:
  зал уходит, а не вступает. Если последний куплет спет хором, разворот ст. 6
  превращается в победу, которой в псалме нет. `final chorus lift` и `key change`
  в Exclude ровно за этим.
- **Бридж — лесенка из трёх ступеней** («Поглянь / Відповідж мені / Освіти мої
  очі»), каждая длиннее предыдущей по словам и короче по действию. Паузы между
  ними нужны; следи, чтобы Suno не сгладил их в ровную строку.
- **Хвост проигрыша.** `[Instrumental break]` помечен безголосым, текст кончается
  `[End]` — именно там на прошлых дублях появлялось «е-е».
- **80 BPM.** У соседей 74 (`a`), 92 (`b`), 84 (`c`) — по темпу вариант посреди,
  и отличать его надо фактурой: пэды, гитарные свеллы и большой хук.
- **Длина.** Девять секций, ожидаемо 3:20–3:40. Если режет — убрать второй
  припев; бридж и аутро не трогать.
