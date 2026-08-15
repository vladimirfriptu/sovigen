---
song: крила-складу-псалом-11
artifact: suno
variant: e
style: cinematic-orchestral
---

# Крила складу (Псалом 11) — вариант e, генерация в Suno

Строки взяты из карточки [[styles/cinematic-orchestral]], хор усилен и вынесен в
середину, добавлена защита от вокализаций по [[craft/suno]].

## Style

```
cinematic orchestral ballad with choir, 4/4 at 66 BPM, solo male baritone over a
single sustained cello in the first verse, violas and low strings joining in the
second, mixed choir singing the written lyrics in the chorus, French horns and
low brass swells, timpani only at the one climax, film-score dynamics with a
single peak and a bare ending, clean straight-tone vocal, syllabic delivery (one
note per syllable), restrained on-the-beat phrasing, no runs, no ad-libs, every
sung sound is a written word, no vocalizations, no vocal fills between lines,
silence where there are no lyrics, instrumental sections stay fully instrumental
with no voice at all, the song ends on the written last line and stops
```

## Exclude Styles

```
melisma, vocal runs, vocal riffs, ad-libs, ooohs and aaahs, whoa-oh chants,
spontaneous worship, oversinging, vocal improvisation, vocalizations, vocalise,
scat singing, wordless choir, choir humming, aahs choir, vocal fills, improvised
vocal tail, outro vocalizing, yeah yeah, hey hey, oh oh, ah ah, eh eh, crowd
vocals, crowd noise, live audience, EDM, trap drums, rock band, drum kit,
electric guitar, epic trailer music, constant crescendo, operatic vibrato,
classical soprano solo, bright major key
```

## Советы по генерации

- **`wordless choir`, `choir humming` и `aahs choir` в Exclude — главное здесь.**
  На слово «choir» Suno почти всегда добавляет бессловесное «а-а-а» под голосом;
  в этом варианте хор поёт только написанные слова припева и молчит везде, где
  их нет.
- **Один пик, и он в середине.** Полное тутти звучит на первом припеве и больше
  не повторяется в такой громкости: второй припев отдан хору без оркестрового
  максимума. Если билд идёт в потолок с первой минуты — дубль мёртв, карточка
  прямо об этом предупреждает.
- **Первый куплет — голос и одна виолончель.** Если струнные вступают сразу
  всей группой, теряется весь запас динамики.
- **Аутро должно быть таким же голым, как первый куплет.** Последние две строки —
  не итог, а тишина после; на пике их петь нельзя.
- **Хвост проигрыша.** `[Instrumental break]` помечен безголосым, текст
  заканчивается `[End]`. Именно в этих местах на прошлых дублях появлялось «е-е».
- **66 BPM** — самый медленный вариант этой песни.
- **Длина.** Девять секций, ожидаемо 3:30–3:50, у верхней границы. Если режет —
  генерировать в два захода и склеивать по границе `[Instrumental break]`.
