---
song: крила-складу-псалом-11
artifact: suno
variant: c
style: imagine-dragons
---

# Крила складу (Псалом 11), вариант `c` — генерация в Suno

Карточки под этот ориентир нет — строки собраны под песню из описания
**Imagine Dragons** в [[styles/references]] (арена-альт-поп, огромные барабаны,
короткий хук, электроника поверх живой ритм-секции) плюс антивыкриковый и
антивокализационный наборы из [[craft/suno]].

## Style

```
arena alt-pop rock, 4/4 at 92 BPM, huge live drums with a floor-tom pattern
driving the whole song, distorted bass, short stabbing guitars, analog synth
pads and electronic layers on top of a live rhythm section, male mid-range lead
singing plainly, big simple four-line hook, group vocals singing the written
lyrics in unison on the last chorus only, words only, no wordless backing
vocals, no crowd noise between lines, clean straight-tone vocal, syllabic
delivery (one note per syllable), restrained on-the-beat phrasing, no runs, no
ad-libs, every sung sound is a written word, no vocalizations, no vocal fills
between lines, silence where there are no lyrics, the instrumental break is
drums and bass with no voice at all, the song ends on the written last line and
stops
```

## Exclude Styles

```
melisma, vocal runs, vocal riffs, ad-libs, ooohs and aaahs, whoa-oh chants,
spontaneous worship, oversinging, vocal improvisation, vocalizations, vocalise,
scat singing, vocal fills, improvised vocal tail, outro vocalizing, yeah yeah,
hey hey, oh oh, ah ah, eh eh, crowd vocals, crowd noise, live audience, audience
shouts, hey shouts, wordless backing vocals, background vocalizations, chanting,
football chant, la-la-la vocals, vocal pads, stadium crowd, festival crowd,
gospel choir, children's choir, trap drums, dubstep drop, autotune, rap verse,
country, americana
```

## Советы по генерации

- 4/4 на 92 BPM, барабаны — главный инструмент; гармонии в куплетах почти нет,
  и так задумано. Если Suno подкладывает под куплеты полноценные аккорды и
  делает из этого поп-балладу, масштаб пропадает — дубль мимо.
- Ждать примерно 2:55, самый короткий из трёх. Резать, скорее всего, не
  придётся; если всё-таки режет — убрать второй `[Chorus]`.
- **Признак провального дубля:** толпа на фоне. Жанр тянет за собой стадион
  сам, поэтому в Style заказано `group vocals … on the last chorus only`, а в
  Exclude стоит целый блок про толпу. Услышал непрерывное «оу» между строк —
  можно не дослушивать.
- Второй признак: голос поверх `[Instrumental break]` или тянущийся хвост после
  последней строки. Проверять первым делом конец песни.
- Хук повторяется трижды дословно и меняться не должен — растёт только
  аранжировка. Если Suno начинает варьировать мелодию хука, вариант теряет своё
  единственное отличие от `a`.
