---
song: освіти-мої-очі-псалом-13
artifact: suno
variant: e
style: cinematic-orchestral
---

# Освіти мої очі (Псалом 13) — вариант e, генерация в Suno

Строки из карточки [[styles/cinematic-orchestral]], доработанные под хор,
который несёт смысл, а не украшает, плюс защита от вокализаций по
[[craft/suno]].

## Style

```
cinematic orchestral ballad with choir, 4/4 at 60 BPM, very slow, solo male
baritone with a single sustained cello in the verses, mixed choir singing the
written lyrics unaccompanied between the verses, low strings entering only in
the second half, full orchestra with horns for one passage and one peak only,
choir silent in the final section, film-score dynamics with a bare ending, clean
straight-tone vocal, syllabic delivery (one note per syllable), restrained
on-the-beat phrasing, no runs, no ad-libs, every sung sound is a written word,
no vocalizations, no vocal fills between lines, silence where there are no
lyrics, instrumental sections stay fully instrumental with no voice at all, the
song ends on the written last line and stops
```

## Exclude Styles

```
melisma, vocal runs, vocal riffs, ad-libs, ooohs and aaahs, whoa-oh chants,
spontaneous worship, oversinging, vocal improvisation, vocalizations, vocalise,
scat singing, wordless choir, choir humming, aahs choir, choir pads, vocal
fills, improvised vocal tail, outro vocalizing, yeah yeah, hey hey, oh oh, ah
ah, eh eh, crowd vocals, crowd noise, live audience, EDM, trap drums, rock band,
drum kit, electric guitar, epic trailer music, constant crescendo, triumphant
ending, operatic vibrato, classical soprano solo, bright major key, chanting
monks, gregorian
```

## Советы по генерации

- **Хор поёт слова и молчит между ними.** `wordless choir`, `choir humming`,
  `aahs choir` и `choir pads` в Exclude обязательны: на слово «choir» Suno
  подкладывает бессловесное «а-а-а» под голос солиста, и тогда вся идея — хор
  как множество спрашивавших раньше — превращается в подложку.
- **Хоровые блоки идут без инструментов.** Это их отличие от всего остального;
  если под ними играют струнные, они перестают звучать как голос из прошлого.
- **Оркестр вступает один раз** — в бридже, на трёх императивах. До этого только
  виолончель и низкие струнные во второй половине.
- **В финале хора нет вовсе.** Ст. 6 поёт один человек: разворот в псалме
  личный. Если хор возвращается на аутро, дубль испорчен по смыслу.
- **`triumphant ending` в Exclude** — псалом обещает, а не празднует.
- **Хвост проигрыша.** `[Instrumental break]` помечен безголосым, текст кончается
  `[End]`.
- **60 BPM** — самый медленный вариант этой песни и всей текущей тройки псалмов.
  На таком темпе пустых тактов много, поэтому разметка важнее обычного.
- **Длина.** Девять секций, но короткие; ожидаемо 3:20–3:40. Если режет — убрать
  `[Choir 2]`, тогда хор вырастет в один шаг вместо двух.
