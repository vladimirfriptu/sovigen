---
song: тепер-устану-псалом-12
artifact: suno
variant: b
style: bad-omens
---

# Тепер устану (Псалом 12) — вариант b, генерация в Suno

Стиль — ориентир владельца **Bad Omens** из [[styles/references]]. Карточки в
`knowledge/styles/` нет, строки собраны под эту песню. Имя группы в промпт не
вписано намеренно.

## Style

```
dark modern alt-metal, 4/4 half-time at 76 BPM, drop-tuned rhythm guitars with
tight palm-muted chugs, live drum kit with heavy snare and real cymbals, deep
bass guitar, cold atmospheric synth pad behind the band, low clean male voice
carrying the narrative verses, one harsh screamed male voice used only for the
short repeated refrain line, sharp contrast between quiet clean sections and
heavy sections, dry mix with room ambience, clean straight-tone vocal, syllabic
delivery (one note per syllable), restrained on-the-beat phrasing, no runs, no
ad-libs, every sung sound is a written word, no vocalizations, no vocal fills
between lines, silence where there are no lyrics
```

## Exclude Styles

```
melisma, vocal runs, vocal riffs, ad-libs, ooohs and aaahs, whoa-oh chants,
spontaneous worship, oversinging, vocal improvisation, vocalizations, vocalise,
scat singing, vocal fills, improvised vocal tail, outro vocalizing, yeah yeah,
hey hey, oh oh, ah ah, eh eh, crowd vocals, crowd noise, live audience, audience
shouts, hey shouts, wordless backing vocals, background vocalizations, chanting,
football chant, la-la-la vocals, vocal pads, guttural growls, pig squeal,
deathcore, blast beats, guitar solo, nu-metal rap, trip-hop, downtempo,
programmed beat, lo-fi drums, Rhodes piano, orchestral strings, gospel choir
```

## Советы по генерации

- **Живой бэнд — условие, а не деталь.** В `Exclude` стоят `trip-hop`,
  `downtempo`, `programmed beat`, `Rhodes piano` не случайно: тёмное с
  программированным битом владелец закрыл словами (см. [[styles/antistyles]]), и
  провальный дубль здесь — именно такой, где вместо барабанщика машина.
- **Жёсткий вокал только на рефрене.** «Хто нам пан?» — единственное место, где
  голос срывается; всё остальное, включая слова Бога, поётся чистым низким
  голосом. Если крик расползётся на куплеты, вариант провален: контраст и есть
  вся драматургия.
- **Обрыв на `Хто нам па—` — кульминация песни.** Слушать надо именно её. Suno
  склонен договорить слово или дотянуть его голосом; если договорил — это
  дубль в мусор, перегенерируй.
- **Verse 5 (слова Господа) — самое тихое место в песне.** Не громче куплета 1.
  Ошибка, которой ждать: Suno выведет его в кульминацию, потому что текст звучит
  как объявление.
- **Проигрыш и аутро размечены `no vocals` и `[End]`** — без них хвост
  дотягивается вокалом на выдержанной гитаре, что здесь особенно заметно.
- **Темп 76 в half-time.** Ощущение должно быть тяжёлым и медленным при живом
  барабанном рисунке. Если Suno сыграет прямые восьмые в темпе — станет
  панк-роком.
- **Длина.** Десять секций, куплеты укорачиваются; ожидаемо 3:10–3:30. Если
  режет — убрать второй `[Refrain]` (тройной), оставив первый и обрыв.
