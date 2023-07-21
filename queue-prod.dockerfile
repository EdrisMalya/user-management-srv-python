FROM python:3.10.5-slim-buster

# create the app user
RUN addgroup --system app && adduser --system --group app

WORKDIR /app

# https://docs.python.org/3/using/cmdline.html#envvar-PYTHONDONTWRITEBYTECODE
# Prevents Python from writing .pyc files to disk
ENV PYTHONDONTWRITEBYTECODE 1

# ensures that the python output is sent straight to terminal (e.g. your container log)
# without being first buffered and that you can see the output of your application (e.g. django logs)
# in real time. Equivalent to python -u: https://docs.python.org/3/using/cmdline.html#cmdoption-u
ENV PYTHONUNBUFFERED 1
ENV ENVIRONMENT prod
ENV TESTING 0
ENV FASTAPI_ENV='production'
ENV MSSQL_DRIVER='ODBC Driver 18 for SQL Server'
ENV MSSQL_DRIVER_PRODUCTION='sql-server-data-source'
ENV MSSQL_LIVE_SERVER='10.0.0.94'
ENV MSSQL_LIVE_DATABASE='PcrLiveUserManagement'
ENV MSSQL_LIVE_USER='pcr_prod'
ENV MSSQL_LIVE_PASS='Pcr@20-22'
ENV POETRY_VERSION='1.1.13'

# install FreeTDS and dependencies
RUN apt-get update \
    && apt-get install curl -y \
    && apt-get install bash -y \
    && apt-get install vim -y \
    && apt-get install dos2unix -y \
    && apt-get install tzdata -y \
    && apt-get install cron -y \
    && apt-get install time -y \
    && apt-get install bc -y \
    && apt-get install --reinstall build-essential -y

ENV TZ="Asia/Kabul"

RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -

#Debian 10
RUN curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list

RUN apt-get update 
RUN ACCEPT_EULA=Y apt-get install -y msodbcsql18
# optional: for unixODBC development headers
RUN apt-get install -y unixodbc-dev

# Install Poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./pyproject.toml ./poetry.lock* /app/

# Project initialization:
# hadolint ignore=SC2046
RUN echo "$FASTAPI_ENV" && poetry version \
    # Install deps:
    && poetry run pip install -U pip \
    && poetry install \
    $(if [ "$FASTAPI_ENV" = 'production' ]; then echo '--no-dev'; fi) \
    --no-interaction --no-ansi \
    # Cleaning poetry installation's cache for production:
    && if [ "$FASTAPI_ENV" = 'production' ]; then rm -rf "$POETRY_CACHE_DIR"; fi


# copy source code
COPY ./ /app

# Fix line endings && execute permissions
RUN dos2unix *.sh scripts/*.* app/*.*
RUN find . -type f -iname "*.sh" -exec chmod +x {} \;
RUN find . -type f -iname "*.py" -exec chmod +x {} \;

RUN chmod +x prod.run.sh

ENV PYTHONPATH=/app

# chown all the files to the app user
RUN chown -R app:app $HOME

# change to the app user
# Switch to a non-root user, which is recommended by Heroku.
USER app

# Run the run script, it will check for an /app/prestart.sh script (e.g. for migrations)
# And then will start Uvicorn
CMD ["./worker-start.sh"]