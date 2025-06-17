# Foodgram

**Foodgram** — это сервис, который позволяет пользователям публиковать рецепты, добавлять понравившиеся рецепты в избранное, подписываться на других авторов и формировать список покупок для выбранных блюд. Проект представляет собой веб-приложение с REST API, реализованным на Django и Django REST Framework.

## Репозиторий - https://github.com/Artfal11/foodgram-st

## Установка и запуск локально

### Шаги установки

1. **Клонируйте репозиторий**:

   ```bash
   git clone https://github.com/Artfal11/foodgram-st
   cd foodgram-st
   ```

2. ** Дублируйте .env.example и переименуйте в .env, затем вставьте нужные данные

3. **Запустите Docker-контейнеры в /infra**:

   ```bash
   docker-compose up --build
   ```

4. **Выполните миграции и соберите статику**:

   ```bash
   docker compose exec backend python manage.py makemigrations
   docker compose exec backend python manage.py migrate
   docker compose exec backend python manage.py collectstatic
   ```

5. **Создайте суперпользователя**:

   ```bash
   docker compose exec backend python manage.py createsuperuser
   ```

6. **Загрузите тестовые данные**:

   ```bash
   docker compose exec backend python manage.py load_ingredients data/ingredients.json
   ```

7. **Доступ к проекту**:

   - Веб-приложение: `http://localhost/`
   - Админ-панель: `http://localhost/admin/`
   - API: `http://localhost/api/`