# Состав и происхождение

- `vendor/BrowseForge`: исходники BrowseForge 2.1.15 из официального release archive. URL и SHA-256 исходного архива сохранены в `config/versions.json`. MIT attribution сохранён в `vendor/BrowseForge/LICENSE` и корневом `LICENSE`.
- `patches/browseforge-socks5-ipv6.patch`: локальное исправление SOCKS5 IPv6 domain destination через `net.JoinHostPort`. В vendored исходниках оно **уже применено**, повторно применять не нужно.
- `bin/mybrowser-camoufox-launch`: текущая проверенная обёртка Linux identity, системных шрифтов, headers/locale, реального Mesa рендеринга, ограничений proxy/WebRTC и Xwayland auth; путь бинарника вычисляется по runtime-каталогу профиля.
- `bin/mybrowser-chromium-launch`: восстановление desktop X11 auth, поиск Chromium в отдельном runtime-каталоге.
- `bin/mybrowser-mcp`: MCP stdio мост к одному localhost-менеджеру, локальный токен, безопасные ошибки служебных вызовов.
- `bin/mybrowser-proxy-direct`: прозрачный TCP-мост к одному приватно настроенному HTTP-прокси, физический IPv4-интерфейс, проверка маршрута, без fallback.
- `scripts/install.py`: сборка менеджера, закреплённая загрузка Camoufox с SHA-256, установка Playwright driver и отдельных user services.
- `config/profiles.example.json`: только названия/runtime/rendering/native policy восьми профилей. Реальных cookies, personas, паролей и хранилищ нет. `proxy_required` сообщает, что исторический тест использовал прокси; реквизиты вручную задаются после создания новых профилей.
- `tests`: локальные проверки и WebGL/control fixtures без аккаунтов.
- `evidence/2026-10-13`: выбранные обезличенные результаты и скриншоты исходной установки; IP на изображениях скрыт до сохранения. Это историческое доказательство, а не результат каждого нового устройства.

Camoufox 156.0.1-beta.36 (Firefox 156) скачивается отдельно. Авторство и лицензии его Firefox/Mozilla-компонентов принадлежат upstream; ссылки доступны в pinned release и самом browser bundle. Chromium runtime опционален и также не включён в Git. Установленные движки можно переиспользовать локально.

Наш код распространяется на условиях корневой MIT-лицензии с сохранением исходного attribution. Публикация этого репозитория не переименовывает upstream-компоненты и не делает их самостоятельной разработкой MyBrowser.
