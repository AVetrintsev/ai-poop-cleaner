# Cleanup

Навык для очистки ненужных ресурсов проекта или системы: контейнеров, временных стендов, кешей и фоновых процессов. Перед удалением проверяет принадлежность ресурсов и действующую работу.

## Установка

Скопируйте **всю папку** [`skills/cleanup`](skills/cleanup/SKILL.md), включая её подкаталоги, в каталог навыков вашего агента:

| Агент | Для всех проектов | Только для выбранного проекта |
| --- | --- | --- |
| Codex | `~/.agents/skills/cleanup` | `<проект>/.agents/skills/cleanup` |
| Claude Code | `~/.claude/skills/cleanup` | `<проект>/.claude/skills/cleanup` |

`~` — домашняя папка пользователя. Для другого агента с поддержкой Agent Skills используйте его каталог навыков.

Пример установки для Codex из корня этого репозитория в PowerShell:

```powershell
$skillsDirectory = Join-Path $HOME '.agents/skills'
$destination = Join-Path $skillsDirectory 'cleanup'
if (Test-Path -LiteralPath $destination) {
    throw 'Навык cleanup уже установлен. Сохраните прежнюю папку вне каталога навыков перед обновлением.'
}
New-Item -ItemType Directory -Path $skillsDirectory -Force | Out-Null
Copy-Item -LiteralPath './skills/cleanup' -Destination $destination -Recurse
```

Для Claude Code замените `.agents/skills` на `.claude/skills`. На Linux/macOS можно скопировать папку файловым менеджером либо из корня репозитория:

```sh
destination="$HOME/.agents/skills/cleanup"
if [ -e "$destination" ] || [ -L "$destination" ]; then
    printf '%s\n' 'Навык cleanup уже установлен; сохраните прежнюю папку вне каталога навыков.'
else
    mkdir -p "$HOME/.agents/skills" && cp -R ./skills/cleanup "$destination"
fi
```

После установки откройте новый чат. Основной навык требует доступа агента к терминалу целевой машины. Вспомогательные скрипты используют Python 3.10+; сборщик Docker также требует доступного Docker CLI. Облачный агент без подключения к вашей машине не сможет очистить её.

## Вызов

В Codex:

```text
$cleanup
$cleanup audit system
$cleanup clean project /path/to/project
$cleanup retire project-name
$cleanup memory
$cleanup prevent
```

В Claude Code используйте `/cleanup` с теми же аргументами. Это запросы агенту в чате, а не команды терминала.

`audit` только собирает сведения; `clean` убирает подтверждённые ненужные ресурсы; `retire` выводит указанный проект из эксплуатации; `memory` работает с расходом RAM и возвратом памяти WSL; `prevent` добавляет проверки жизненного цикла в выбранный проект. Удаление постоянных данных требует явного указания.

Для обновления сохраните старую папку `cleanup` вне каталогов обнаружения навыков и скопируйте новую целиком. Для удаления навыка удалите только его установленную папку.

Лицензия: [Apache-2.0](LICENSE).
