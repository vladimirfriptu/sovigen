---
song: крила-складу-псалом-11
artifact: suno
variant: a
style: bad-omens
---

# Крила складу (Псалом 11), вариант `a` — генерация в Suno

Карточки под этот ориентир нет — строки собраны под песню из описания
**Bad Omens** в [[styles/references]] (низкий строй, живая ритм-секция,
атмосферные подкладки, контраст чистого и жёсткого вокала) плюс общий
антивокализационный набор из [[craft/suno]].

## Style

```
dark alternative metal ballad, live band, 6/8 at 76 BPM with a half-time heavy
chorus, down-tuned electric guitars, real drum kit with deep toms, ambient
atmospheric pads under the band, male lead singing low and clean in the verses
with one controlled harsh shout section in the bridge, clean straight-tone vocal,
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
shouts, hey shouts, wordless backing vocals, background vocalizations, chanting,
vocal pads, guttural death growls, unintelligible screaming, blast beats,
metalcore breakdown squeals, EDM, trap drums, autotune, gospel choir, orchestral
strings, country, americana, pop production
```

## Советы по генерации

- 6/8 на 76 BPM: песня качается, а не марширует, и это её главное отличие от
  `c`. Если Suno выдаёт ровный 4/4 — перегенерируй, размер здесь несущий.
- Ждать примерно 3:10. Если режет — убрать третий `[Chorus]` (тот, что после
  моста), а не куплет: припев здесь важнее повторами, но три раза он уже
  прозвучал.
- **Признак провального дубля:** жёсткий вокал вылез за пределы `[Bridge]`.
  Куплеты обязаны быть низкими и чистыми, иначе теряется контраст, ради
  которого взят этот ориентир — можно останавливать прослушивание сразу.
- Второй признак: голос в `[Instrumental break]` или после `[End]`. Разметка
  против этого стоит, но проверять в первую очередь именно хвост проигрыша —
  владелец ловил там «е-е» на прошлом заходе.
- Припев не должен ускоряться и не должен становиться выше: он работает как
  удар, а не как подъём. Если Suno вытягивает его в анфем — дубль мимо.
