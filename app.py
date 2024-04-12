from flask import Flask, jsonify, request, make_response
from estrutura_banco_de_dados import Postagem, Autor, app, db
import json
import jwt
from datetime import datetime, timedelta
from functools import wraps

def token_obrigatorio(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Verificar se o tokem foi enviado
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'mensagem': 'Token não foi incluído!'}, 401)
        # Se temos um token, validar o acesso acessando o banco de dados
        try:
            resultado = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            autor = Autor.query.filter_by(id_autor = resultado['id_autor']).first()
        except:
            return jsonify({'mensagem': 'Token não foi incluído!'}, 401)
        return f(autor, *args, **kwargs)
    return decorated


@app.route('/login')
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response('Login inválido', 401, {'WWW-Autheticate': 'Basic realm="Login obrigatório"'})
    usuario = Autor.query.filter_by(nome=auth.username).first()
    if not usuario:
        return make_response('Login inválido', 401, {'WWW-Autheticate': 'Basic realm="Login obrigatório"'})
    if auth.password == usuario.senha:
        token = jwt.encode({'id_autor': usuario.id_autor, 'exp': datetime.utcnow() + timedelta(minutes=30)}, app.config['SECRET_KEY'])
        return jsonify({'token': token})
    return make_response('Login inválido', 401, {'WWW-Autheticate': 'Basic realm="Login obrigatório"'})


@app.route('/')
@token_obrigatorio
def obter_autores(autor):
    autores = Autor.query.all()
    lista_de_autores = []

    for autor in autores:
        autor_atual = {}
        autor_atual['id_autor'] = autor.id_autor
        autor_atual['nome'] = autor.nome
        autor_atual['email'] = autor.email
        autor_atual['senha'] = autor.senha
        autor_atual['admin'] = autor.admin

        lista_de_autores.append(autor_atual)

    return jsonify({'autores': lista_de_autores})

@app.route('/autores/<int:id_autor>', methods=['GET'])
@token_obrigatorio
def obter_autores_por_id(autor, id_autor):
    autor = Autor.query.filter_by(id_autor=id_autor).first()

    if not autor:
        return jsonify({'mensagem': 'Autor não encontrado!'})

    autor_atual = {}
    autor_atual['id_autor'] = autor.id_autor
    autor_atual['nome'] = autor.nome
    autor_atual['email'] = autor.email
    autor_atual['senha'] = autor.senha
    autor_atual['admin'] = autor.admin

    return jsonify({'autor': autor_atual})

@app.route('/autores', methods=['POST'])
@token_obrigatorio
def novo_autor(autor):
    novo_autor = request.get_json()
    autor = Autor(id_autor=novo_autor['id_autor'], nome=novo_autor['nome'], email=novo_autor['email'], senha=novo_autor['senha'], admin=novo_autor['admin'])

    db.session.add(autor)
    db.session.commit()

    return jsonify({'mensagem': 'Usuário criado com sucesso'})

@app.route('/autores/<int:id_autor>', methods=['PUT'])
@token_obrigatorio
def alterar_autor(autor, id_autor):
    autor_a_ser_alterado = request.get_json()
    autor = Autor.query.filter_by(id_autor=id_autor).first()

    if not autor:
        return jsonify({'mensagem': 'Autor não encontrado!'})
    
    try:
        autor.nome = autor_a_ser_alterado['nome']
    except:
        pass
    try:
        autor.email = autor_a_ser_alterado['email']
    except:
        pass
    try:
        autor.senha = autor_a_ser_alterado['senha']
    except:
        pass
    try:
        autor.admin = autor_a_ser_alterado['admin']
    except:
        pass

    db.session.commit()

    return jsonify({'mensagem': 'Usuário alterado com sucesso!'})



@app.route('/autores/<int:id_autor>', methods=['DELETE'])
@token_obrigatorio
def excluir_autor(autor, id_autor):
    autor_existente = Autor.query.filter_by(id_autor=id_autor).first()

    if not autor_existente:
        return jsonify({'mensagem': 'Autor não encontrado!'})

    db.session.delete(autor_existente)
    db.session.commit()

    return jsonify({'mensagem': 'Usuário excluido com sucesso.'})

@app.route('/postagem')
@token_obrigatorio
def obter_postagem(autor):
    # Pegar todos os dados da tabela postagem
    postagens = Postagem.query.all()
    lista_de_postagens = []
    for postagem in postagens:
        postagem_atual = {}
        postagem_atual['titulo'] = postagem.titulo
        postagem_atual['id_autor'] = postagem.id_autor
        
        lista_de_postagens.append(postagem_atual)
    
    return jsonify({'postagens': lista_de_postagens})


@app.route('/postagem/<int:id_postagem>', methods=['GET'])
@token_obrigatorio
def obter_postagem_por_id(autor, id_postagem):
    # Pegar uma postagem pelo id e deve ser somente a primeira requisição 
    postagem = Postagem.query.filter_by(id_postagem=id_postagem).first()
    
    if not postagem:
        return jsonify(f'Postagem não encontrada!')
    
    postagem_atual = {}
    postagem_atual['titulo'] = postagem.titulo
    postagem_atual['id_autor'] = postagem.id_autor

    return jsonify({'postagem': postagem_atual})


@app.route('/postagem', methods=['POST'])
@token_obrigatorio
def nova_postagem(autor):
    nova_postagem = request.get_json()
    postagem = Postagem(titulo=nova_postagem['titulo'], id_postagem=nova_postagem['id_autor'])

    db.session.add(postagem)
    db.session.commit()

    return jsonify({'mensagem': 'Postagem criado com sucesso.'}, 200)

@app.route('/postagem/<int:id_postagem>', methods=['PUT'])
@token_obrigatorio
def alterar_postagem(autor, id_postagem):
    postagem_a_alterar = request.get_json()
    postagem = Postagem.query.filter_by(id_postagem=id_postagem).first()

    if not postagem:
        return jsonify({'mensagem': 'A postagem não foi encontrado'})

    try:
        postagem.titulo = postagem_a_alterar['titulo']
    except:
        pass
    try:
        postagem.id_autor = postagem_a_alterar['id_autor']
    except:
        pass

    return jsonify({'mensagem': 'Postagem alterado com sucesso.'})


@app.route('/postagem/<int:id_postagem>', methods=['DELETE'])
@token_obrigatorio
def excluir_postagem(autor, id_postagem):
    postagem_existente = Postagem.query.filter_by(id_postagem=id_postagem).first()

    if not postagem_existente:
        return jsonify({'mensagem': 'Postagem não foi encontrada.'})
    
    db.session.delete(postagem_existente)
    db.session.commit()

    return jsonify({'mensagem': 'Postagem excluida com sucesso.'})
    


app.run(host='0.0.0.0', port=5000, debug=False)