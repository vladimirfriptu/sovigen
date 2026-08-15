---
song: крила-складу-псалом-11
artifact: suno
variant: h
style: youth-guitar
---

# Крила складу (Псалом 11) — вариант h, генерация в Suno

Спокойная разновидность карточки [[styles/youth-guitar]]: перебор вместо боя,
76 BPM, подпевка терциями, без роста состава. Защита от вокализаций применена
всеми тремя слоями — разметка в тексте, положительная формулировка здесь,
блок запретов в Exclude. Общий порядок — [[craft/suno]].

## Style

```
gentle acoustic folk-pop, 4/4 at 76 BPM, unhurried, two fingerpicked acoustic
guitars with a melodic second line, no percussion at all, warm male mid-range
lead singing softly and close to the microphone, a second voice joining in
thirds on the choruses, two voices at most and never more, words only, every
sung sound is a written word, no vocalizations, no vocal fills between lines,
silence where there are no lyrics, live take feel as if recorded in one room
with two people, no studio polish, clean straight-tone vocal, syllabic delivery
(one note per syllable), restrained on-the-beat phrasing, no runs, no ad-libs
```

## Exclude Styles

```
melisma, vocal runs, vocal riffs, ad-libs, ooohs and aaahs, whoa-oh chants,
spontaneous worship, oversinging, vocal improvisation, EDM, trap drums,
electronic drums, drum kit, cajon, percussion, autotune, processed vocals,
stadium reverb, arena anthem, pop production, electric guitar solo, orchestral
strings, gospel choir, children's choir, country, americana, ska, punk,
double-time, crowd vocals, crowd noise, live audience, audience shouts,
hey shouts, wordless backing vocals, background vocalizations, chanting,
football chant, la-la-la vocals, vocal pads, vocalizations, vocalise,
scat singing, vocal fills, improvised vocal tail, outro vocalizing, yeah yeah,
hey hey, oh oh, ah ah, eh eh, big chorus, anthem, crescendo, build-up
```

## Советы по генерации

- **Медленный темп — это больше пустых тактов, то есть больше соблазна для
  вокализаций.** Именно здесь «е-е» в конце проигрыша и «я-я-я» поверх припева
  вероятнее всего. Поэтому каждый инструментальный кусок в тексте помечен тегом
  с `no vocals`, а текст заканчивается `[End]`. Если вокализации всё равно есть —
  дубль не спасать: слои защиты исчерпаны, нужна перегенерация.
- **Никакой ритм-секции.** `cajon`, `percussion` и `drum kit` стоят в Exclude
  намеренно, хотя карточка их обычно допускает: держат только две гитары.
- **Состав не растёт.** Это главное отличие от быстрых вариантов той же
  карточки: третий припев берёт выше голосом, а не громче составом. `crescendo`,
  `build-up`, `big chorus` и `anthem` в Exclude ровно за этим. Если к финалу
  вступает толпа — вариант провалился, потому что он про то, что никого больше
  не прибавилось.
- **Не более двух голосов.** В Style это сказано дважды (`a second voice joining
  in thirds`, `two voices at most and never more`) — на «group vocals» Suno
  добавляет людей, а здесь их взять неоткуда.
- **76 BPM** — вдвое медленнее варианта `g` (108) и заметно медленнее `d` (100).
  Быстрее 84 вариант теряет смысл: он существует ради того, чтобы те же слова
  припева прозвучали не ударом, а вполголоса.
- **Длина.** Восемь секций, ожидаемо 3:00–3:20. Резать нечего: инструментальный
  проигрыш перед третьим припевом — единственная пауза, и она несёт форму.
