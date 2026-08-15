---
song: тепер-устану-псалом-12
artifact: suno
variant: c
style: ruah
---

# Тепер устану (Псалом 12) — вариант c, генерация в Suno

Стиль — ориентир владельца **Ruah** из [[styles/references]]. Карточки в
`knowledge/styles/` нет, строки собраны под эту песню. Название коллектива в
промпт не вписано; слово `worship` не вписано тоже — оно тянет за собой
распевки (см. [[craft/suno]]), поэтому жанр назван как
`contemporary Christian ballad`.

## Style

```
intimate contemporary Christian ballad in Ukrainian, 6/8 at 68 BPM, fingerpicked
steel-string acoustic guitar, soft upright-style bass entering late, brushed
snare and light room percussion only, warm male lead voice close to the
microphone, a second male voice joining in plain unison on the last two
refrains, small chamber arrangement, no build to a big ending, dry warm mix as
if recorded in one room, clean straight-tone vocal, syllabic delivery (one note
per syllable), restrained on-the-beat phrasing, no runs, no ad-libs, second
voice singing the written lyrics in unison, words only, no wordless backing
vocals, no crowd noise between lines, every sung sound is a written word, no
vocalizations, no vocal fills between lines, silence where there are no lyrics
```

## Exclude Styles

```
melisma, vocal runs, vocal riffs, ad-libs, ooohs and aaahs, whoa-oh chants,
spontaneous worship, oversinging, vocal improvisation, vocalizations, vocalise,
scat singing, vocal fills, improvised vocal tail, outro vocalizing, yeah yeah,
hey hey, oh oh, ah ah, eh eh, crowd vocals, crowd noise, live audience, audience
shouts, hey shouts, wordless backing vocals, background vocalizations, chanting,
football chant, la-la-la vocals, vocal pads, arena anthem, stadium reverb,
gospel choir, children's choir, orchestral strings, electric guitar solo, EDM,
electronic drums, autotune, processed vocals, key change, big drum build
```

## Советы по генерации

- **6/8 и 68 BPM — это качание, а не марш.** Единственный вариант тройки в
  трёхдольном размере; если Suno выдаст 4/4, вариант перестаёт отличаться от
  остальных по ощущению.
- **Никакого билда.** `arena anthem`, `key change`, `big drum build` в Exclude
  ради этого: рефрен повторяется четыре раза и каждый следующий должен быть
  **тише** предыдущего. Провальный дубль — тот, где к финалу вырастает бэнд.
- **Второй голос — только в унисон и только словами.** На двух последних
  рефренах. Если он начнёт подкладывать «а-а» под первый голос, это ровно та
  беда, на которую владелец жаловался; перегенерируй.
- **Verse 4 почти шёпотом.** «Тепер устану» здесь — самое тихое место песни, а
  не кульминация. Это весь смысл варианта.
- **Проигрыш после второго рефрена размечен `no vocals`, песня закрыта `[End]`** —
  в камерной аранжировке хвост особенно тянет на распевку.
- **Длина.** Одиннадцать коротких секций, ожидаемо 3:00–3:20. Если режет — убрать
  третий рефрен (после Verse 3), но тогда пропадает шаг «один голос → два
  голоса», и укорочение строф читается хуже.
