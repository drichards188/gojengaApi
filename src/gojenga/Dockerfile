FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11
WORKDIR /app
COPY . /app
RUN mkdir ~/.aws
RUN echo "[default]\nregion = us-east-2\noutput = JSON" > ~/.aws/config
RUN echo "[default]\naws_access_key_id = AKIAYQOGHDACV3RONOWP\naws_secret_access_key = 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" > ~/.aws/credentials
RUN cat ~/.aws/credentials
RUN pip install -r requirements.txt
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]