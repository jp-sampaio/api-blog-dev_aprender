from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Criar uma API com flask;
app = Flask(__name__)

# Criar uma instância de SQLALckemy e modificar algumas configurações (secret_key, url database);
app.config['SECRET_KEY'] = 'fsd349$#hd445'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'

db = SQLAlchemy(app)

# Tipar o db como sqlalchemy para evitar problemas futuros
db:SQLAlchemy

# Definir uma estrutura da tabela postagem;
# id_postagem, titulo, autor
class Postagem(db.Model):
    __tablename__ = 'postagem'
    id_postagem = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String)
    id_autor = db.Column(db.Integer, db.ForeignKey('autor.id_autor'))

# Definir uma estrutura da tabela autor.
# id_autor, nome, email, senha, admin, postagens
class Autor(db.Model):
    __tablename__ = 'autor'
    id_autor = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String)
    email = db.Column(db.String)
    senha = db.Column(db.String)
    admin = db.Column(db.Boolean)
    postagens = db.relationship('Postagem')

def inicializar_banco():
    # Executar o comando para criar o banco de dados 
    with app.app_context():
        db.drop_all() # Apaga qualquer estrutura previa que possa existir
        db.create_all() # Cria todas as tabelas anexadas no db
        # Criar usuários adminstradores
        autor = Autor(nome='João Paulo', email='jpsampaio@gmail.com', senha='senha123', admin=True) # Cria a instância de autor
        # autor2 = Autor(nome='maria', email='maria@gmail.com', senha='senha123678', admin=False)
        db.session.add(autor) # Adiciona autor no banco de dados
        db.session.commit() # Salva os camondos realizados

if __name__ == "__main__":
    inicializar_banco()