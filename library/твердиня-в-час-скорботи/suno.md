---
song: твердиня-в-час-скорботи
artifact: suno
style: casting-crowns
---

# Твердиня в час скорботи — генерация в Suno

## Style

```
contemporary Christian pop-rock ballad, male baritone lead, narrative delivery,
4/4 at 74 BPM, unhurried and grounded, fingerpicked acoustic guitar intro
building to full band by the second chorus, warm analog drums played by a human,
electric guitar swells kept low in the mix, close dry vocal with a small room
sound, clean straight-tone vocal, syllabic delivery (one note per syllable),
restrained on-the-beat phrasing, no runs, no ad-libs
```

## Exclude Styles

```
melisma, vocal runs, vocal riffs, ad-libs, ooohs and aaahs, whoa-oh chants,
spontaneous worship, oversinging, vocal improvisation, EDM, trap drums,
stadium reverb, arena anthem, orchestral bombast, gang vocals, choir pads,
double-time drums, marching snare
```

## Советы по генерации

Размер 4/4 на 74 BPM: псалом качается, а не марширует. Маршевость здесь —
главный риск, потому что половина текста про суд над народами; отсюда в Exclude
попали `marching snare` и `double-time drums`. Если дубль пошёл в темп марша,
это слышно уже на Verse 2 — такой дубль можно не дослушивать.

Второй риск — стадион. В прошлом заходе по этому псалому владельцу не зашёл
именно звук, поэтому в Style стоит `close dry vocal with a small room sound`, а
в Exclude — `stadium reverb`, `arena anthem`, `choir pads` и `gang vocals`.
Припев должен вырасти составом инструментов, а не размером зала. Финальный
припев остаётся тем же бэндом, никакого хора.

Длина: четыре куплета, три припева, пре-припев, бридж и аутро — на 74 BPM это
примерно 3:20–3:40, то есть у верхней границы безопасного. Если Suno обрежет
аутро или скомкает финал — убрать второй `[Chorus]` (тот, что между Verse 3 и
бриджем) и сгенерировать заново; арка от этого не ломается, потому что мотив
ст. 10 возвращается в финале.

За чем следить в вокале: бридж («Помилуй мене») — то место, где солист чаще
всего срывается в распевку. Если на этой строке появились мелизмы, дубль не
спасать, а перегенерировать.
