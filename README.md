# Метод анализа иерархий 

## Шаги для запуска:
1. Скачать код проекта 
2. Настройть среду для запуска - потребуется Python3.8, а также библиотеки, указанные в requirements.txt
3. [Optional] Возможно потребуется миграция схем БД
    Для этого, находясь в корневой директории проекта, необходимо запустить следующие команды:
    >```python manage.py makemigrations```
    >```python manage.py migrate```
4. Для запуска, находясь в корневой директории проекта, введите команду:
    >```python mnage.py runserver```
    По умолчанию сервис запустится на хосте 127.0.0.1, порт 8000

**Важно**: для отладки необходимо установить параметр ***DEBUG=True*** в файле analytical_hierarchical_process/setting.py
При ***DEBUG=False*** файлы static отключаются. Чтобы использовать их так же, как и при отладке, необходимо осуществлять запуск командой:
>```python manage.py runserver --insecure```