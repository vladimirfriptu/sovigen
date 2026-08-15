---
song: цар-навіки-віків
artifact: suno
variant: d
style: experiment-kobzar-duma
---

# Цар навіки віків — вариант d, генерация в Suno

Стиль экспериментальный: карточки в `knowledge/styles/` нет, строки собраны с
нуля. Если вариант зайдёт — из него пишется карточка, до тех тех пор он живёт
только здесь.

## Style

```
Ukrainian kobzar duma, epic sung recitation, solo male baritone chest voice,
bandura and lute-family plucked strings only, modal minor with a drone, free
unmetered rhythm following the speech, no drums and no percussion at all, no
chord progression in the pop sense, long declamatory phrases with pauses between
them, dry close recording as if in a room, one voice and one instrument, clean
straight-tone vocal, syllabic delivery (one note per syllable), speech-rhythm
phrasing, no runs, no ad-libs
```

## Exclude Styles

```
melisma, vocal runs, vocal riffs, ad-libs, ooohs and aaahs, whoa-oh chants,
spontaneous worship, oversinging, vocal improvisation, EDM, trap drums, drum kit,
percussion, bass guitar, electric guitar, piano, strings section, choir, pop
structure, chorus, verse-chorus form, western folk, celtic, country, americana,
bluegrass, gypsy, balalaika, stadium reverb, cinematic build
```

## Советы по генерации

- **Здесь нет припева и нет размера.** Дума не марширует и не качается — ритм
  задаёт речь. Поэтому в Style стоит `free unmetered rhythm` и BPM не указан
  сознательно: как только Suno поставит сетку, вариант превратится в западную
  фолк-баллáду и смысл пропадёт.
- **Провальный дубль слышно на первой строке:** если вошли барабаны, бас или
  гитарный аккомпанемент — не слушай дальше. Должны быть только голос и щипковый
  инструмент. `celtic`, `country`, `americana`, `bluegrass` стоят в Exclude
  потому, что Suno почти всегда тащит «фолк» в эту сторону; `balalaika` — потому
  что на слово «bandura» он норовит подставить русский аналог.
- **Подача — рассказ, не пение.** Пять куплетов идут одинаково, без нарастания;
  единственный подъём — пятый («А Господь дивився»). Если солист начнёт
  распевать зачин, дубль мёртв.
- **Рифмы в тексте нет намеренно.** Suno иногда пытается «дотянуть» строку до
  рифмы, растягивая последний слог — это тот же дефект, что мелизма, и лечится
  только перегенерацией.
- **Длина.** Шесть секций без повторов, ожидаемо 3:00–3:30. Если режет — убирать
  третий куплет нельзя (там весь хищник); лучше сгенерировать в два захода и
  склеить перед четвёртым куплетом, там естественная пауза.
- **Произношение.** «зостається», «порахував», «заступника» — длинные слова в
  речитативе; проверь, что они не проглочены на затухании фразы.
