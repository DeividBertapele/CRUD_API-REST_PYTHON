from flask import Flask, request, jsonify
from flask_pydantic_spec import FlaskPydanticSpec, Response, Request
from pydantic import BaseModel, Field
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage
from typing import Optional
from itertools import count


app = Flask(__name__)
spec = FlaskPydanticSpec('flask', title='CRUD API_REST')
spec.register(app)
database = TinyDB(storage=MemoryStorage)
c = count()


class QueryPessoa(BaseModel):
    id: Optional[int]
    nome: Optional[str]
    idade: Optional[int]


class Pessoa(BaseModel):
    id: Optional[int] = Field(default_factory=lambda: next(c))
    nome: str
    idade: int


class Pessoas(BaseModel):
    pessoas: list[Pessoa]
    count: int


@app.get('/pessoas')  # Rota, endpoint, recurso etc...
@spec.validate(query=QueryPessoa, resp=Response(HTTP_200=Pessoas)
)
def buscar_pessoas():
    """Retorna todas as Pessoas da base de dados."""
    query = request.context.query.dict(exclude_none=True)
    todas_as_pessoas = database.search(
        Query().fragment(query)
    )
    return jsonify(
        Pessoas(
            pessoas=todas_as_pessoas,
            count=len(todas_as_pessoas)
        ).dict()
    )


@app.get('/pessoas/<int:id>') # com ID para buscar a pessoa
@spec.validate(resp=Response(HTTP_200=Pessoa))
def buscar_pessoa(id):
    """Retorna todas as Pessoas {id} da base de dados."""
    try:
        pessoa = database.search(Query().id == id)[0]
    except IndexError:
        return {'message': 'Pessoa not found!'}, 404
    return jsonify(pessoa)


@app.post('/pessoas')
@spec.validate(
    body=Request(Pessoa), resp=Response(HTTP_201=Pessoa)
)
def inserir_pessoa():
    """Insere uma Pessoa no banco de dados."""
    body = request.context.body.dict()
    database.insert(body)
    return body


@app.put('/pessoas/<int:id>')
@spec.validate(body=Request(Pessoa), resp=Response(HTTP_201=Pessoa))
def altera_pessoa(id):
    """Altera uma Pessoa no banco de dados."""
    Pessoa = Query()
    body = request.context.body.dict()
    database.update(body, Pessoa.id == id)
    return jsonify(body)


@app.delete('/pessoas/<int:id>')
@spec.validate(resp=Response('HTTP_204'))
def deleta_pessoa(id):
    """Remove uma Pessoa do banco de dados."""
    database.remove(Query().id == id)
    return jsonify({})



if __name__ == "__main__":
    app.run(debug=True)