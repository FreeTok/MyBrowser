# Проверки 13 октября 2026

Исходная рабочая установка: BrowseForge 2.1.15 с SOCKS5 IPv6 fix, Camoufox 156.0.1-beta.36, Linux x86_64. Данные перенесены выборочно, без IP, реквизитов прокси, токенов и cookies.

Два завершённых Pixelscan через реальный MCP, затем повтор после закрытия/открытия:

| Проверка | Firefox 1, hardware | Firefox 3, llvmpipe MSAA 8 |
|---|---|---|
| Browser | зелёная | зелёная |
| Location | зелёная | зелёная |
| Proxy | Proxy detected | Proxy detected |
| Fingerprint | No masking detected | No masking detected |
| Bot check | No automated behavior detected | No automated behavior detected |
| Итог | inconsistent, 4/5 | inconsistent, 4/5 |

WebGL hashes: `c6285c24c33b38d2ed08361330469b7d` и `e60c75e040248500b1e5f250269ceec8`. Отличаются, повторный запуск сохранил значения. Четыре режима также давали разные пиксели на локальной тестовой сцене; unlimited uniqueness не проверена и не обещается.

HTTP-прокси работал через прозрачный локальный мост, закреплённый на физическом интерфейсе. Глобальный Hiddify VPN остальных приложений не менялся. Смена IP и совпадение контрольного адреса с браузерами проверены локально; адреса в доказательствах заменены метками/булевыми результатами. География согласована: Italy, Europe/Rome, it-IT.

Ответ Pixelscan `/s/api/ci`: `user_type: hosting`, `isHostingProvider: true`, `isPublicProxy: true`. Остаточная причина 4/5 связана с классификацией предоставленного адреса. Браузерная настройка не меняет репутацию IP. Другой адрес потребует новой проверки, успех заранее не гарантирован.

При остановке моста новая HTTPS-страница не загрузилась напрямую. В локальном STUN-сценарии с `proxy_only` ICE gathering завершился без кандидатов и UDP-пакетов. Это ограниченные сценарии, не доказательство отсутствия любых сетевых утечек. DNS имени proxy server использует системный resolver.

Полное отключение WebRTC раньше сопровождалось незавершённым сканом. Для завершения одновременно изменены маршрут и WebRTC policy; отдельная причина старого зависания не установлена.

Сканер, ответы API и вердикты не подменялись. Текст IP скрывался только перед сохранением изображения.

Доказательства:

- [Маршрут браузеров](../evidence/2026-10-13/browser-route.json), [прямой транспорт](../evidence/2026-10-13/direct-transport.json), [счётчики физических соединений](../evidence/2026-10-13/direct-route-proof.json).
- [Конфигурация и совпадение IP](../evidence/2026-10-13/configured-direct.json), [классификация адреса](../evidence/2026-10-13/network-classification.json).
- [Отказ без fallback](../evidence/2026-10-13/fail-closed.json), [STUN-сценарий](../evidence/2026-10-13/webrtc.json).
- [Снимок Firefox 1](../evidence/2026-10-13/proxy-direct-gpu-restart.png), [снимок Firefox 3](../evidence/2026-10-13/proxy-direct-software-restart.png).

Проверка репозитория и отдельного runtime описывается в `evidence/2026-10-13/repository-verification.json` после локального smoke test. Она подтверждает переносимость запуска/MCP, не новый полный Pixelscan.
