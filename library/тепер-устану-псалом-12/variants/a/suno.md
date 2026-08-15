---
song: тепер-устану-псалом-12
artifact: suno
variant: a
style: imagine-dragons
---

# Тепер устану (Псалом 12) — вариант a, генерация в Suno

Стиль — ориентир владельца **Imagine Dragons** из [[styles/references]].
Карточки в `knowledge/styles/` нет, поэтому строки ниже собраны под эту песню, а
не взяты готовыми. Имя группы в промпт не вписано намеренно: Suno на имена
исполнителей реагирует плохо, и описание работает надёжнее.

## Style

```
arena alt-pop rock, 4/4 at 92 BPM, huge live floor toms and thundering tribal
drum pattern, deep analog synth pad and low sub bass under a real rhythm section,
single distorted guitar riff, wide dynamic contrast between a hushed near-spoken
verse and a wall-of-sound chorus, male mid-range lead voice, one lower calm male
voice for the bridge, big room drums with natural decay, clean straight-tone
vocal, syllabic delivery (one note per syllable), restrained on-the-beat
phrasing, no runs, no ad-libs, every sung sound is a written word, no
vocalizations, no vocal fills between lines, silence where there are no lyrics
```

## Exclude Styles

```
melisma, vocal runs, vocal riffs, ad-libs, ooohs and aaahs, whoa-oh chants,
spontaneous worship, oversinging, vocal improvisation, vocalizations, vocalise,
scat singing, vocal fills, improvised vocal tail, outro vocalizing, yeah yeah,
hey hey, oh oh, ah ah, eh eh, crowd vocals, crowd noise, live audience, audience
shouts, hey shouts, wordless backing vocals, background vocalizations, chanting,
football chant, la-la-la vocals, vocal pads, gospel choir, children's choir,
EDM drop, trap drums, autotune, rap verse, country, americana, orchestral
strings
```

## Советы по генерации

- **Темп 92, 4/4, барабаны — главный инструмент.** Если ритм-секция выходит
  мелкой и аккуратной, вариант провален: весь смысл жанра здесь в том, что
  припев физически больше куплета.
- **Перевёртыш надо услышать.** Первые два припева — «Устань, Господи, устань!»
  голосом снизу; третий — «Тепер устану» тем же напевом, но спокойно и от
  первого лица. Если Suno споёт третий припев так же надрывно, как первые два,
  главный приём песни не сработал — это провальный дубль.
- **Бридж должен быть почти проговорён,** ниже по регистру, с минимальной
  подложкой. Это единственное место, где звучит голос Бога, и он не кричит.
- **Проигрыш после второго припева отмечен `no vocals` прямо в теге** — именно
  там владелец слышал «е-е» в конце проигрыша. Если голос всё же дотягивает
  хвост, перегенерируй, а не правь Exclude: разметка — первый слой защиты,
  запреты — третий и самый слабый.
- **Длина.** Одиннадцать секций, ожидаемо 3:05–3:25. Если режет — убрать второй
  `[Pre-Chorus]` целиком, а не припев: припевов ровно три и они несут перевёртыш.
- **Аутро тихое.** Песня не заканчивается победой; если финал выведет в
  стадионный анфем, смысл ст. 9 потерян.
