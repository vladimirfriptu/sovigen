---
song: псалом-14
artifact: suno
variant: f
style: bad-omens
model: v6-wild
generation_phase: explore
---

# Псалом 14 — генерация в Suno, вариант `f`

## Режим генерации

`v6-wild` / `explore`: ищем убедительный перелом из 5/4 в медленный 4/4 и
смену дистанции голоса, а не готовый мастер с первой попытки. Удачную форму
перенести в обычный `v6`; гроул, лишний возврат риффа или вокал в паузе править
точечно по секции.

Карточки под ориентир **Bad Omens** нет; строка собрана по
[[styles/references]] и общим правилам [[craft/suno]].

## Аудит v6

Первый промпт перегружал модель сразу жанром alt-metal, двумя размерами, двумя
голосами, паузой и запретом harsh-вокала. Размеры и драматургический перелом
оставлены, но жанр сдвинут в progressive hard rock: так больше шансов получить
тяжесть без гроула. Спетые технические строки про «первый» и «второй» голос
заменены образом оборвавшейся за столом речи.

## Style

```
dark progressive alternative hard rock in Ukrainian, first half in uneven 5/4
at 96 BPM, low guitar ostinato and tense melodic bass, dry acoustic drum kit
with deep toms and tight kick, one restrained atmospheric texture behind the
live trio, low male baritone singing clean and nearly conversational, every
lyric fully intelligible, heavy chorus made by guitars and drums rather than
harsh vocals, sudden complete stop for two beats after the second chorus,
second half changes permanently to sparse straight 4/4 with a different distant
clean male baritone, clean guitar and low sustained bass in the outro, no return
of the first ostinato or first singer, every sung sound is a written word, no
vocalizations, no vocal fills between lines, silence where there are no lyrics,
clean straight-tone vocal, syllabic delivery (one note per syllable), restrained
on-the-beat phrasing, no runs, no ad-libs, song ends on the written final word
and stops
```

## Exclude Styles

```
melisma, vocal runs, vocal riffs, ad-libs, ooohs and aaahs, whoa-oh chants,
spontaneous worship, oversinging, vocal improvisation, vocalizations, vocalise,
scat singing, vocal fills, improvised vocal tail, outro vocalizing, yeah yeah,
hey hey, oh oh, ah ah, eh eh, crowd vocals, crowd noise, live audience,
audience shouts, wordless backing vocals, background vocalizations, chanting,
vocal pads, guttural growls, screaming, unintelligible harsh vocals, blast
beats, metalcore breakdown, breakdown squeals, djent chugs, industrial metal,
trap drums, electronic drums, trip-hop, downtempo, Rhodes piano, gospel choir,
orchestral strings, key change, triumphant final chorus
```

## Советы по генерации

- Первый проход — `v6-wild`, финальное уточнение найденного направления — `v6`.
- Первая половина — 5/4 на 96 BPM, вторая — разреженный прямой 4/4. Ориентир —
  **Bad Omens**, но звук смещён в progressive hard rock, без имени в `Style` и
  без скрима: слова угнетателя должны быть разборчивы.
- Ожидаемая длина около 3:10. Если режет, убрать первый повтор припева; нельзя
  сокращать бридж, потому что именно там меняются голос и размер.
- После двух ударов полной тишины первый рифф и первый певец не возвращаются.
  Если Suno делает обычный breakdown и затем возвращает куплет — форма сломана.
- **Провальный дубль:** гроул или крик. Тяжесть должна идти от строя гитар и
  ритма; неразборчивый вокал превращает конкретное признание в жанровый шум.
