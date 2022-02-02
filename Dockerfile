FROM ubuntu:20.04

WORKDIR /app

COPY ./ nextline-graphql
RUN pip install --upgrade pip
RUN pip install ./nextline-graphql
RUN rm -rf ./nextline-graphql

CMD ["uvicorn", "--factory", "--host", "0.0.0.0", "nextlinegraphql:create_app"]
