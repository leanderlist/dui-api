# Verwenden des offiziellen Python-Images als Basis
FROM python:3

# Setzen des Arbeitsverzeichnisses im Container
WORKDIR /api

# Kopieren der Anwendungsdateien in das Arbeitsverzeichnis
COPY api.py /api/

# Installieren der Abhängigkeiten der Anwendung
RUN apt-get update
RUN apt-get install curl
RUN curl -LsS https://downloads.mariadb.com/MariaDB/mariadb_repo_setup | bash
RUN apt-get update
RUN apt-get install -y libmariadb3 libmariadb-dev
RUN pip install mysql-connector-python
RUN pip install mariadb
RUN pip install -U discord.py
# Starten der API beim Starten des Containers
CMD ["python3", "bot.py"]
