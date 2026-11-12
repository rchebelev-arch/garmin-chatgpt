# Garmin Connect и Railway

Сервис читает тренировки через официальный Garmin Connect Personal API. Доступ к данным защищён отдельным ключом сервиса.

## Развёртывание

1. Загрузите содержимое этой папки в приватный репозиторий GitHub. В существующем проекте Railway выберите **New → GitHub Repo** и подключите репозиторий. Если сервис уже создан, обновите его исходный репозиторий.
2. В **Variables** добавьте `GARMIN_API_KEY` со значением персонального ключа Garmin и `API_TOKEN` с отдельным случайным секретом. Создать отдельный секрет можно командой `openssl rand -hex 32`. Вводите секреты в Railway. Если использовались `GARMIN_EMAIL` и `GARMIN_PASSWORD`, удалите эти переменные из сервиса.
3. Примените изменения через **Deploy**. В **Settings → Networking** нажмите **Generate Domain**. Если Railway запрашивает команду запуска, укажите `uvicorn main:app --host 0.0.0.0 --port $PORT`.
4. Откройте `https://ВАШ-ДОМЕН/health`. Ответ `{"status":"ok"}` подтверждает запуск приложения.
5. В терминале проверьте доступ к Garmin. Замените адрес доменом из Railway. По запросу введите значение `API_TOKEN`.

   ```bash
   printf 'API_TOKEN: '
   read -rs garmin_bridge_token
   printf '\n'
   printf 'header = "Authorization: Bearer %s"\n' "$garmin_bridge_token" |
     curl -fsS --config - 'https://ВАШ-ДОМЕН/activities?limit=1'
   unset garmin_bridge_token
   ```

## Подключение к ChatGPT через Actions

Если в вашем аккаунте доступно создание или редактирование приватного GPT с Actions, откройте редактор GPT и добавьте Action. Вставьте содержимое `action-openapi.yaml`, заменив адрес в `servers` на домен сервиса. В **Authentication** выберите **API Key → Bearer** и введите `API_TOKEN`. Сохраните GPT с доступом **Only me** и попросите показать последнюю тренировку. Эта настройка действует в выбранном GPT. OpenAI планирует вывести Custom GPTs из эксплуатации 11 декабря 2026 года. Срок и доступные варианты проверьте по уведомлению в аккаунте.

[Garmin Personal API](https://developer.garmin.com/gc-developer-program/personal/personal-api/)  
[Настройка GPT Actions](https://help.openai.com/en/articles/9442513-configuring-actions-in-gpts)  
[График вывода Custom GPTs](https://help.openai.com/en/articles/20001519-custom-gpt-retirement-and-migration-faq)
