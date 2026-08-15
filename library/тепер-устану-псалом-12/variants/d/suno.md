---
song: тепер-устану-псалом-12
artifact: suno
variant: d
style: hillsong
---

# Тепер устану (Псалом 12) — вариант d, генерация в Suno

Строки из карточки [[styles/hillsong]] плюс защита от вокализаций по
[[craft/suno]]. Ориентир — Hillsong, первый уровень [[styles/references]]; имя
группы в промпт не вписано, Suno фильтрует имена исполнителей.

## Style

```
contemporary Christian pop-rock ballad, 4/4 at 76 BPM, anthemic chorus, male
lead with supporting group vocals singing the written lyrics only, atmospheric
electric guitar swells, wide reverb pads, the peak falls on the bridge and the
final section is the quietest in the song, clean straight-tone vocal, syllabic
delivery (one note per syllable), restrained on-the-beat phrasing, no runs, no
ad-libs, every sung sound is a written word, no vocalizations, no vocal fills
between lines, silence where there are no lyrics, instrumental sections stay
fully instrumental with no voice at all, the song ends on the written last line
and stops
```

## Exclude Styles

```
melisma, vocal runs, vocal riffs, ad-libs, ooohs and aaahs, whoa-oh chants,
spontaneous worship, oversinging, vocal improvisation, vocalizations, vocalise,
scat singing, vocal fills, improvised vocal tail, outro vocalizing, yeah yeah,
hey hey, oh oh, ah ah, eh eh, crowd vocals, crowd noise, live audience, audience
shouts, wordless backing vocals, background vocalizations, chanting, vocal pads,
key change, final chorus lift, triumphant ending, gospel choir, EDM, trap drums,
autotune, orchestral strings, country, americana
```

## Советы по генерации

- **Самое важное: песня не должна закончиться победой.** Пик приходится на
  бридж, а последняя секция — самая тихая. `key change`, `final chorus lift` и
  `triumphant ending` вынесены в Exclude намеренно. Если Suno выводит финал на
  подъём, дубль испорчен по смыслу, а не по звуку: псалом кончается тем, что
  вокруг ходят те же самые.
- **Бридж — единственное место, где поют во весь голос.** Это слова Бога; всё
  остальное — просьба.
- **`spontaneous worship` держи в Exclude целиком** — карточка предупреждает,
  что жанр сам тянет распевки.
- **Подпевка поёт слова**, а не «о-о-о»: положительная формулировка в Style плюс
  антивыкриковый блок в Exclude.
- **Хвост проигрыша.** `[Instrumental break]` помечен безголосым, текст кончается
  `[End]` — на прошлых дублях именно там появлялось «е-е».
- **76 BPM.** У соседей по песне 92 (`a`), 76 half-time (`b`) и 68 (`c`) — с `b`
  темп совпадает, но фактуры несравнимы: там тяжёлые гитары без припева, здесь
  пэды и хук.
- **Длина.** Девять секций, ожидаемо 3:20–3:40. Если режет — убрать второй
  припев, но не бридж и не аутро: на них держится вся конструкция.
