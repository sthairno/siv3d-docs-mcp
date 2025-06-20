FROM python:3.12 AS base

COPY ./requirements.txt /requirements.txt
RUN pip install --no-cache-dir --upgrade -r /requirements.txt

FROM base AS data_builder

COPY ./siv3d.docs /siv3d.docs
COPY ./scripts/make_data.py /scripts/make_data.py

RUN DOCS_DIR=/siv3d.docs OUT_DIR=/data python /scripts/make_data.py make

FROM base AS restapi

WORKDIR /restapi

COPY --from=data_builder /data /data
COPY ./src /restapi

CMD ["uvicorn", "restapi_main:app", "--host", "0.0.0.0", "--port", "80", "--proxy-headers", "--env-file", "/restapi/.env"]
