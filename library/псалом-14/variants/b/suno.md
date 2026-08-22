---
song: псалом-14
artifact: suno
variant: b
style: cinematic-orchestral
---

# Псалом 14 — генерация в Suno, вариант `b`

## Style

```
cinematic orchestral ballad in Ukrainian, 4/4 at 62 BPM, solo male baritone over
sustained strings, first verse almost bare with a single low cello line, strings
widening verse by verse, choir entering only in the middle, French horns and low
brass swells for one peak and one only, timpani, a full stop into two bars of
complete silence before the fifth verse, then unaccompanied voice, film-score
dynamics with the peak placed before the ending rather than at it, the last two
sections quieter than the opening, every sung sound is a written word, no
vocalizations, no vocal fills between lines, silence where there are no lyrics,
clean straight-tone vocal, syllabic delivery (one note per syllable), restrained
on-the-beat phrasing, no runs, no ad-libs
```

## Exclude Styles

```
melisma, vocal runs, vocal riffs, ad-libs, ooohs and aaahs, whoa-oh chants,
spontaneous worship, oversinging, vocal improvisation, vocalizations, vocalise,
scat singing, vocal fills, improvised vocal tail, outro vocalizing, yeah yeah,
hey hey, oh oh, ah ah, eh eh, crowd vocals, crowd noise, live audience, audience
shouts, wordless backing vocals, background vocalizations, chanting, la-la-la
vocals, vocal pads, EDM, trap drums, electronic drums, autotune, processed
vocals, key change, triumphant final chorus, big final tutti, rising outro
```

## Советы по генерации

- Карточка [[styles/cinematic-orchestral]], но с одной поправкой против
  обычного: **пик стоит не в конце, а в четвёртой строфе**, и после него музыка
  снимается. Строка `peak placed before the ending` в `Style` держит именно это.
- 62 BPM, 4/4 — самый медленный из трёх вариантов. Ни одна строфа не
  повторяется, припева нет, поэтому длина держится на темпе: ждать около трёх
  минут.
- Тег `[Break: full stop, two bars of silence...]` — самое хрупкое место дубля.
  Suno почти наверняка попробует заполнить эту паузу голосом или струнными.
  Если заполнил — генерь заново, промпт тут ни при чём.
- Резать при обрезке нечего: строфы идут по стихам подряд. Если не влезает —
  генерить в два захода и склеивать по паузе перед пятой строфой, шов там
  и так задуман.
- **Что делает дубль неудачным:** оркестр, растущий к финалу. Псалом
  заканчивается тем, чего ещё нет; тутти в конце превращает его в триумф.
  Услышал, что последняя строфа громче четвёртой — можно не дослушивать.
