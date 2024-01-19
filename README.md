#  Ulearn Django - итоговый проект курса
Данный проект является итоговым проектом курса по Python на Ulearn.me.

## Развертывание в Docker
Для развертывания проекта в Docker нужно использовать контейнер, расположенный по адресу `ghcr.io/kexogg/ulearnproject:main`
### Переменные окружения
```
DB_HOST - адрес сервера PostgreSQL
DB_USER - пользователь базы данных
DB_NAME - название базы данных
DB_PASSWORD - пароль пользователя базы данных
DJANGO_SECRET_KEY - секретный ключ Django
```
Опционально:
```
DB_PORT - порт сервера PostgreSQL (по умолчанию 5432)
DEBUG - режим отладки Django (по умолчанию False)
```
### Пример развертки с помощью `docker-compose.yml`:
```yaml
version: '3.8'
services:
  ulearn-project:
    image: ghcr.io/kexogg/ulearnproject:main
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      DB_HOST: "db"
      DB_USER: "dbuser"
      DB_NAME: "mydb"
      DB_PASSWORD: "mypassword"
      DJANGO_SECRET_KEY: "mysecretkey" # Не забудьте изменить секретный ключ!
  db:
    image: postgres:16
    restart: unless-stopped
    environment:
      POSTGRES_USER: "dbuser"
      POSTGRES_DB: "mydb"
      POSTGRES_PASSWORD: "mypassword"
    volumes:
      - ./db:/var/lib/postgresql/data
```
### Пример развертки с помощью `docker run`:
```bash
docker run -d -p 8000:8000 \
    -e DB_HOST=db \
    -e DB_USER=dbuser \
    -e DB_NAME=mydb \
    -e DB_PASSWORD=mypassword \
    -e DJANGO_SECRET_KEY=mysecretkey \ 
    ghcr.io/kexogg/ulearnproject:main
```