![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Jenkins](https://img.shields.io/badge/Jenkins-D24939?style=for-the-badge&logo=jenkins&logoColor=white)
![Ansible](https://img.shields.io/badge/Ansible-EE0000?style=for-the-badge&logo=ansible&logoColor=white)
![ELK](https://img.shields.io/badge/ELK-005571?style=for-the-badge&logo=elastic-stack&logoColor=white)
![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-F46800?style=for-the-badge&logo=grafana&logoColor=white)
![cAdvisor](https://img.shields.io/badge/cAdvisor-4285F4?style=for-the-badge&logo=google&logoColor=white)
![Alertmanager](https://img.shields.io/badge/Alertmanager-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)


# Identidock

Приложение генерирует уникальное изображение (монстрика)<br>
на основе введённой пользователем строки.<br>
![Пример изображения](./screenshots/screenshot1.png)<br><br>

---
## Как запускать
1. Выполнить `git clone`.<br>
2. Перейти в каталог identiproxy и выполнить сборку `docker build -t proxy:1.0 .` .<br>
3. Поправить  **`docker-compose.yml`** файл,<br>
указав актуальный IP адрес для переменной `NGINX_HOST`<br>
4. Выполнить команду: `docker-compose up -d`<br>

Для настройки CI\CD (Jenkins)
5. Перейти в каталог identijenk и выполнить сборку `docker-compose up -d`.<br>
Далее потребуется настроить задачу. Пример для shell скрипта расположен в каталоге identijenk.<br><br>

Для настройки сбора метрик (cAdvisor + Prometheus)<br>
6. Перейти в каталог metrics и выполнить сборку `docker-compose up -d`


### Проверка работоспособности

- Приложение: http://localhost:80
- Kibana: http://localhost:5601
- Jenkins: http://localhost:8090
- Elasticsearch: http://localhost:9200
- cAdvisor: http://localhost:8085
- Prometheus: htpp://localhost:9090

---
### Технологии и инструменты
Работа основана на материале книги "Использование Docker".<br>

| Категория | Технологии |
|-----------|-----------|
| Языки | Python, Bash |
| Веб-фреймворк | Flask |
| Контейнеризация | Docker, Docker Compose |
| CI/CD | Jenkins, GitHub |
| Мониторинг | ELK Stack (Elasticsearch, Logstash, Kibana), Logspout |
| Сбор метрик | cAdvisor, Prometheus, Grafana, Alertmanager |
| Оркестрация | Ansible |
| Базы данных | Redis |
| Веб-сервер | Nginx, uWSGI |

***Сборка и запуск python приложения*** (identidock.py) в Docker-контейнере.<br>
Приложение написано на *Flask*. В качестве сервера используется *uWSGI*.<br><br>

***DEV/UNIT/PROD*** скрипт cmd.sh определяет в каком окружении будет <br>
запускаться приложение.<br><br>

***CI/CD pipeline*** использован *Jenkins*.<br>
Использован подход Continuous Deployment. Задача проверяет репозиторий GitHub.<br>
Если в коде приложения/docker файлах есть изменения -> поднимаются контейнеры<br>
в тестовом окружении и запускаются тесты.<br>
Если тесты прошли образы заливаются в репозиторий DockerHub.<br>
При запуске приложения берутся образы из DockerHub и происходит сборка<br>
в PROD окружении.<br><br>

![Общая цепочка взаимодействия](./screenshots/screenshot.png)<br><br>

***Мониторинг логов*** использован стек *ELK*.<br>
*Logspout* - собирает логи всех приложений на хосте.<br>
*Logstash* - фильтрует логи.<br>
*Elasticsearch* - хранит логи, создает индексы для быстрого поиска.<br>
*Kibana* - отображает логи для анализа.<br>

![Пример мониторинга](./screenshots/screenshot3.png)<br><br>

***Сбор метрик*** использована связка Prometheus + Grafana + Alertmanager.<br>
*cAdvisor* - собирает метрики всех контейнеров на хосте (CPU, память, сеть, диски)<br>
*Prometheus* - хранение и анализ временных рядов метрик, язык запросов PromQL<br>
*Grafana* - визулизация метрик, построение дашбордов<br>
*Alertmanager* - обработка и отправка алертов


***Настройка на нескольких хостах*** использован *Ansible*.<br>
Необходимо установить ansible на целевую машину - хост.<br>
Прокинуть ssh ключи на целевые машины (target, где должно рабоать приложение),<br>
скорректировать файл hosts (inventory) и актуализировав `NGINX_HOST`<br>
в `identidock.yml`.<br>
Далее можно будет вызвать:

```bash
ansible-playbook -i hosts identidock.yml
```
<br>Приложение будет развернуто на target хостах.

***Ротирование логов*** использован logrotate Linux.<br>
Если не настроено ротирование логов для Docker,<br>
то очень быстро закончится место на диске.<br>
В ОС Linux рекомендуется выполнить скрипт<br>
docker_logrotate.sh c root правами.

---
### Структура файлов
- **identidock/** - исходный код Flask-приложения
- **identijenk/** - конфигурация Jenkins
- **identiproxy/** - конфигурация Nginx (балансировщик)
- **monitoring/** - конфигируция ELK (настройка парсинга логов, данные ELK, Logspout)
- **metrics/** - конфигурация метрик (cAdvisor, Prometheus, Grafana, Alertmanager)
- **usefull_scripts/** - опциональные скрипты для разового запуска
- **ansible_configuration/** - Ansible плейбуки для деплоя
- **screenshots/** - скриншоты для README
- **common.yml** - версии образов для всех сервисов

---
### Известные проблемы и их решение

**Windows ошибка**: "exec /cmd.sh: no such file or directory".<br>
**Причина:** CRLF окончания строк в скриптах.<br>
**Решение:** Конвертируйте скрипты в формат LF<br>

```powershell
(Get-Content cmd.sh) -join "`n" | Set-Content -NoNewline cmd.sh
```

***Ошибка доступа к Docker Hub***
**Причина:** Не настроены credentials для Jenkins.<br>
**Решение:** Укажите свои логин/пароль и репозиторий в Jenkins-задаче.<br>
<br>

---
## Ссылки
"Using Docker" by Adrian Mouat - https://files.znu.edu.ua/files/Bibliobooks/Inshi70/0051001.pdf
