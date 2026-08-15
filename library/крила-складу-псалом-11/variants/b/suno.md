---
song: крила-складу-псалом-11
artifact: suno
variant: b
style: casting-crowns
---

# Крила складу (Псалом 11), вариант `b` — генерация в Suno

База — строки карточки [[styles/casting-crowns]], дополненные размером и
темпом под эту песню и полным антивокализационным набором из [[craft/suno]].

## Style

```
contemporary Christian pop-rock ballad, male baritone lead, narrative delivery,
4/4 at 70 BPM, acoustic guitar intro building to full band by the third verse
and pulling back to acoustic at the end, warm analog drums with brushes early,
upright bass, one room live take feel, clean straight-tone vocal, syllabic
delivery (one note per syllable), restrained on-the-beat phrasing, no runs, no
ad-libs, single lead voice throughout with no backing singers, every sung sound
is a written word, no vocalizations, no vocal fills between lines, silence where
there are no lyrics, the instrumental break has no voice at all, the song ends
on the written last line and stops
```

## Exclude Styles

```
melisma, vocal runs, vocal riffs, ad-libs, ooohs and aaahs, whoa-oh chants,
spontaneous worship, oversinging, vocal improvisation, vocalizations, vocalise,
scat singing, vocal fills, improvised vocal tail, outro vocalizing, yeah yeah,
hey hey, oh oh, ah ah, eh eh, crowd vocals, crowd noise, live audience, audience
shouts, hey shouts, wordless backing vocals, background vocalizations, chanting,
la-la-la vocals, vocal pads, EDM, trap drums, arena anthem, stadium reverb,
gospel choir, distorted guitars, double-time
```

## Советы по генерации

- 4/4 на 70 BPM — самый медленный из трёх и единственный разговорный. Голос
  должен звучать так, будто человек отвечает собеседнику, а не залу.
- Ждать примерно 3:20 — четыре куплета длиннее обычного. Если режет: сократить
  `[Verse 4]` до четырёх строк (убрать «У Нього для них є вогонь і вітер, / і
  Він не забуде долити») — рефрен и ст. 7 при этом остаются.
- **Признак провального дубля:** повторяющаяся строка «Я сховався в Господі — і
  я не полечу» спета каждый раз одинаково громко. Она обязана расти от куплета
  к куплету, это единственное движение песни; ровный рефрен — мимо.
- Второй признак: появились подпевающие голоса. В этом варианте один голос от
  начала до конца, поэтому в Style стоит `single lead voice`, а хоровые строки
  из карточки `youth-guitar` сюда сознательно не перенесены.
- Прямую речь друга Suno иногда поёт с той же интонацией, что и ответ. Если
  разница интонаций совсем не читается — второй дубль, текст в порядке.
