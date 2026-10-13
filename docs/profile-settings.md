# Настройки нативного профиля

Профиль: `<MYBROWSER_HOME>/profiles/<id>/browser-data/CamoufoxNative/`.

`persona.json` создаётся при первом запуске и остаётся локальным. UA соответствует Firefox 156; системные Linux-шрифты сохраняют реальные метрики. Audio seed закреплён за профилем. Для нового профиля seed выбирается по пути профиля, затем хранится в файле: перенос существующего полного профиля с `persona.json` сохраняет seed.

`rendering.json`:

```json
{"schema": 1, "backend": "hardware"}
```

Поддержаны `hardware`, `llvmpipe`, `llvmpipe-msaa8`, `softpipe`, дополнительный диагностический `llvmpipe-sse2`. Значения vendor/renderer/limits/extensions берутся у реального backend. JS `readPixels` не подменяется. Новые профили получают один из четырёх режимов; коллизии возможны. Предустановленные Firefox 1–4 закрепляют четыре разных режима.

`native-policy.json`, при необходимости:

```json
{"schema": 1, "fonts": "system", "audio": "seeded", "navigator": "pinned", "webrtc": "proxy_only"}
```

`fonts: bundled`, `audio: native`, `navigator: native`, `ipv4_only: true` сохранены для диагностики. Они не проверены как лучший вариант для текущего скана. По умолчанию — системные шрифты, seeded audio и pinned navigator. `webrtc: proxy_only` применяется только при наличии прокси; иначе WebRTC доступен штатно. Прокси без этого параметра отключает WebRTC.

Правьте файлы при закрытом браузере. Управляемые prefs в `user.js` обновляются обёрткой; прочие prefs сохраняются. Профильные и групповые прокси учитываются с тем же приоритетом, что у менеджера. Устаревшие WebGL-метки очищаются, чтобы не оставаться в `prefs.js`.
