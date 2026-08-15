---
song: тепер-устану-псалом-12
artifact: suno
variant: e
style: cinematic-orchestral
---

# Тепер устану (Псалом 12) — вариант e, генерация в Suno

Строки из карточки [[styles/cinematic-orchestral]], доработанные под антифон
двух хоров, плюс защита от вокализаций по [[craft/suno]].

## Style

```
cinematic orchestral ballad with choir, 4/4 at 64 BPM, antiphonal: a dense low
male choir singing in unison against a solo baritone and a mixed choir, low
strings under the solo verses, full orchestra and mixed choir entering only
once at the single peak, French horns and timpani at that peak only, everything
bare again afterwards, film-score dynamics with one climax, clean straight-tone
vocal, syllabic delivery (one note per syllable), restrained on-the-beat
phrasing, no runs, no ad-libs, every sung sound is a written word, no
vocalizations, no vocal fills between lines, silence where there are no lyrics,
instrumental sections stay fully instrumental with no voice at all, the song
ends on the written last line and stops
```

## Exclude Styles

```
melisma, vocal runs, vocal riffs, ad-libs, ooohs and aaahs, whoa-oh chants,
spontaneous worship, oversinging, vocal improvisation, vocalizations, vocalise,
scat singing, wordless choir, choir humming, aahs choir, vocal fills, improvised
vocal tail, outro vocalizing, yeah yeah, hey hey, oh oh, ah ah, eh eh, crowd
vocals, crowd noise, live audience, EDM, trap drums, rock band, drum kit,
electric guitar, epic trailer music, constant crescendo, triumphant ending,
operatic vibrato, classical soprano solo, bright major key, chanting monks,
gregorian
```

## Советы по генерации

- **Два хора должны звучать по-разному, иначе вариант бессмыслен.** Хор
  нечестивых (куплеты 2 и 3) — низкий, плотный, в унисон; ответ (припев) —
  смешанный хор с оркестром, выше и чище. Если оба спеты одним и тем же
  составом, слушать нечего.
- **Ответ не громче, а чище.** В тексте это сказано прямо строкой «не голосніше
  за них», и в Style стоит `entering only once at the single peak`. Пик — на
  ст. 6, не в финале.
- **`wordless choir`, `choir humming`, `aahs choir` в Exclude обязательны** — на
  слово «choir» Suno почти всегда добавляет бессловесное «а-а-а». Хор здесь поёт
  только написанные слова.
- **`chanting monks` и `gregorian` тоже в Exclude:** на «antiphonal» Suno охотно
  уезжает в григорианику, и тогда пропадает современный масштаб.
- **Финал не разрешается.** `triumphant ending` в Exclude: последняя секция —
  соло почти без сопровождения, ст. 9, где всё как было.
- **Хвост проигрыша.** `[Instrumental break]` безголосый, текст кончается
  `[End]`.
- **64 BPM** — самый медленный из пяти вариантов этой песни.
- **Длина.** Десять секций, ожидаемо 3:40–4:00 — за верхней границей. Если
  режет: убрать третий куплет (повтор реплики нечестивых), тогда хор станет
  многолюдным в один шаг вместо двух; всё остальное несёт форму.
