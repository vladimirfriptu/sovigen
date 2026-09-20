---
song: псалом-14
artifact: suno
variant: d
style: newsboys
model: v6-wild
generation_phase: explore
---

# Псалом 14 — генерация в Suno, вариант `d`

## Режим генерации

`v6-wild` / `explore`: ищем не ещё один аккуратный поп-рок, а неожиданный
сухой гитарный хук, который удержит тревогу псалма при светлом составе. Если хук
работает, перенести этот дубль в обычный `v6` и там точечно убрать лишние
вокальные вставки или поправить секцию, не пересобирая удачную песню целиком.

Карточки под ориентир **Newsboys** нет; строка собрана по
[[styles/references]] и общим правилам [[craft/suno]].

## Аудит v6

Первый промпт одновременно требовал 136 BPM, длинные строки и большой припев,
из-за чего модель могла либо проглатывать слова, либо уходить в слишком
торжественный Christian-rock. Темп снижен до 128 BPM, а звук стал суше и уже:
короткий power-pop вместо почти стадионного припева. В тексте укорочены самые
плотные строки, смысл ожидания сохранён.

## Style

```
lean urgent Christian power-pop in Ukrainian, 4/4 at 128 BPM, alert and watchful
rather than cheerful, warm male baritone-tenor singing plainly, tight dry live
drums, palm-muted electric guitar in the verses, bright open power chords only
in the choruses, melodic bass, no synths, steady pulse that never drops, compact
memorable chorus with one restrained double of the lead singing the exact
written words, bridge reduced to one clean guitar while keeping the same tempo,
final chorus firm but unresolved, short dry ending, every sung sound is a
written word, no vocalizations, no vocal fills between lines, silence where
there are no lyrics, clean straight-tone vocal, syllabic delivery (one note per
syllable), restrained on-the-beat phrasing, no runs, no ad-libs
```

## Exclude Styles

```
melisma, vocal runs, vocal riffs, ad-libs, ooohs and aaahs, whoa-oh chants,
spontaneous worship, oversinging, vocal improvisation, vocalizations, vocalise,
scat singing, vocal fills, improvised vocal tail, outro vocalizing, yeah yeah,
hey hey, oh oh, ah ah, eh eh, crowd vocals, crowd noise, live audience,
audience shouts, hey shouts, wordless backing vocals, background vocalizations,
chanting, football chant, la-la-la vocals, vocal pads, gospel choir, orchestral
strings, arena rock, stadium chorus, glossy synth pop, ballad, half-time
breakdown, slow bridge, EDM, trap drums, autotune, key change, triumphant ending
```

## Советы по генерации

- Первый проход — `v6-wild`, финальное уточнение найденного направления — `v6`.
- 128 BPM, 4/4. Ориентир — **Newsboys**, но звук смещён в сухой гитарный
  power-pop; название группы в `Style` не используется. Энергия должна читаться
  как бодрствование, не как веселье.
- Ждать 2:50–3:10. Если Suno растягивает — убрать второй обычный припев, но не
  финальный: только финальный договаривает условие ст. 7.
- Бридж тише по составу, но **не медленнее**. Если появился half-time или
  балладная яма, обратный ход псалма потеряет движение.
- **Провальный дубль:** припев звучит так, будто спасение уже пришло. Он должен
  быть требовательным ожиданием; мажорная победная кода противоречит тексту.
