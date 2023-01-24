FROM ubuntu:20.04

WORKDIR /app

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git

COPY ./ nextline-graphql
RUN pip install --upgrade pip
RUN pip install ./nextline-graphql
RUN pip install nextline-rdb>=0.1
RUN pip install uvicorn
RUN rm -rf ./nextline-graphql

CMD ["uvicorn", "--lifespan", "on", "--factory", "--host", "0.0.0.0", "nextlinegraphql:create_app"]
