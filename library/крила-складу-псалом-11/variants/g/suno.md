---
song: крила-складу-псалом-11
artifact: suno
variant: g
style: youth-guitar
---

# Крила складу (Псалом 11) — вариант g, генерация в Suno

Строки взяты из карточки [[styles/youth-guitar]] уже после её исправления:
подпевка описана через слова, антивыкриковый блок стоит в Exclude целиком.
Общий рецепт — [[craft/suno]].

## Style

```
acoustic guitar singalong, 4/4 at 108 BPM, bright strummed acoustic guitar with a
capo, warm male mid-range lead singing plainly, group vocals singing the written
lyrics in unison on every chorus and growing louder each time, words only, no
wordless backing vocals, no crowd noise between lines, every sung sound is a
written word, no vocalizations, no vocal fills between lines, silence where there
are no lyrics, light cajon and hand percussion only, simple three-chord harmony,
live take feel as if recorded in one room with several people, no studio polish,
clean straight-tone vocal, syllabic delivery (one note per syllable), restrained
on-the-beat phrasing, no runs, no ad-libs
```

## Exclude Styles

```
melisma, vocal runs, vocal riffs, ad-libs, ooohs and aaahs, whoa-oh chants,
spontaneous worship, oversinging, vocal improvisation, EDM, trap drums, electronic
drums, autotune, processed vocals, stadium reverb, arena anthem, pop production,
electric guitar solo, orchestral strings, gospel choir, children's choir, country,
americana, ska, punk, double-time, crowd vocals, crowd noise, live audience,
audience shouts, hey shouts, wordless backing vocals, background vocalizations,
chanting, football chant, la-la-la vocals, vocal pads, vocalizations, vocalise,
scat singing, vocal fills, improvised vocal tail, outro vocalizing, yeah yeah, hey
hey, oh oh, ah ah, eh eh
```

## Советы по генерации

- **Первое, что слушать, — фон припева.** Именно на этом стиле Suno сажал толпу,
  которая выкрикивает «оу» и тянет «о-о-о» поверх текста. Здесь против этого
  работают три слоя сразу: теги `no vocals` на всех инструментальных кусках и
  `[End]` в конце текста, положительная формулировка `words only … silence where
  there are no lyrics` в Style и блок `crowd vocals … eh eh` в Exclude. Если
  выкрики всё равно есть — дубль не спасать, а перегенерировать: это тот самый
  дефект, ради которого строки и добавлены.
- **108 BPM** — быстрее варианта `d` (100) и «Ти бачиш» (104), по верхней
  границе карточки. Песня должна идти легко: текст короткий, тянуть его незачем.
- **Пре-припева нет.** Куплет сразу переходит в припев; припев самый короткий в
  песне, четыре строки, и он не меняется ни разу. Всё движение — в количестве
  голосов: первый почти сольный, последний хоровой.
- **Бридж — перекличка построчно**, лид и ответ. Единственное место, где голоса
  разделены; в припевах они поют одно и то же.
- **Аутро.** Первые две строки — один голос, последние две — все. Если аутро
  споют хором целиком, пропадёт то, ради чего оно написано.
- **Живая комната, не студия.** `autotune`, `processed vocals`, `pop production`
  держи в Exclude — гладкий продакшн убивает жанр.
- **Длина.** Семь секций, ожидаемо 2:40–3:00. Резать нечего и не нужно.
