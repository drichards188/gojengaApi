#
FROM python:3.11

#
WORKDIR /code

#
COPY ./requirements.txt /code/requirements.txt

#
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

#
COPY . /code

#place build vars in build command. --build-args="ID=248djad" --build-args="KEY=2fdpoad"
ARG ID=placeholder
ARG KEY=placeholder

#
RUN mkdir ~/.aws

RUN touch ~/.aws/credentials

RUN echo "[default]\naws_access_key_id = $ID\naws_secret_access_key = $KEY\nregion = us-east-2" > ~/.aws/credentials

#
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
