FROM simonsobs/ocs:v0.9.0

WORKDIR /app

COPY ./ nextline-graphql
RUN pip install --upgrade pip
RUN pip3 install ./nextline-graphql
RUN rm -rf ./nextline-graphql

CMD ["uvicorn", "--factory", "--host", "0.0.0.0", "nextlinegraphql:create_app"]
