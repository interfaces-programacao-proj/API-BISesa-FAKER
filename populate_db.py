from sqlalchemy import create_engine, Column, Integer, String, Date, CHAR, ForeignKey, Text, DECIMAL
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import date, timedelta, datetime
from faker import Faker
import random

# Conexao com SQLite
DATABASE_URL = 'sqlite:///banco_teste.db'

Base = declarative_base()
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()
fake = Faker('pt_BR')

class Cidade(Base):
    __tablename__ = 'cidades'
    cidade_id = Column(Integer, primary_key=True)
    nome = Column(String(50), nullable=False)

class Enfermidade(Base):
    __tablename__ = 'enfermidades'
    enfermidade_id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text)
    gravidade = Column(String(20))

class Paciente(Base):
    __tablename__ = 'pacientes'
    paciente_id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    data_nascimento = Column(Date, nullable=False)
    sexo = Column(CHAR(1))
    cidade_id = Column(Integer, ForeignKey('cidades.cidade_id'))
    faixa_etaria = Column(String(20), nullable=False)

class Tratamento(Base):
    __tablename__ = 'tratamentos'
    tratamento_id = Column(Integer, primary_key=True)
    paciente_id = Column(Integer, ForeignKey('pacientes.paciente_id'))
    enfermidade_id = Column(Integer, ForeignKey('enfermidades.enfermidade_id'))
    data_inicio = Column(Date, nullable=False)
    data_fim = Column(Date)
    custo_total = Column(DECIMAL(10, 2), nullable=False)
    cidade_id = Column(Integer, ForeignKey('cidades.cidade_id'))
    duracao_dias = Column(Integer)

Base.metadata.create_all(engine)

# Inserir cidades
cidades_ceara = ["Fortaleza", "Caucaia", "Juazeiro do Norte", "Maracanaú", "Sobral",
                 "Crato", "Itapipoca", "Maranguape", "Quixadá", "Aquiraz"]
session.bulk_save_objects([Cidade(cidade_id=i+1, nome=nome) for i, nome in enumerate(cidades_ceara)])
session.commit()

# Enfermidades com graus e gravidades simplificadas
gravidade_map = {
    "Grau 1": "Leve",
    "Grau 2": "Moderada",
    "Grau 3": "Grave",
    "Grau 4": "Muito Grave"
}

enfermidades_com_grau = [
    {"nome": "Dengue", "graus": {
        "Grau 1": "Febre com sintomas inespecíficos.",
        "Grau 2": "Sinais de alarme.",
        "Grau 3": "Sinais iniciais de choque.",
        "Grau 4": "Choque profundo."
    }},
    {"nome": "Chikungunya", "graus": {
        "Grau 1": "Fase aguda.", "Grau 2": "Fase subaguda.", "Grau 3": "Fase crônica."
    }},
    {"nome": "Zika", "graus": {
        "Grau 1": "Assintomático.", "Grau 2": "Sintomas leves.", "Grau 3": "Riscos fetais."
    }}
]

id_counter = 1
for enf in enfermidades_com_grau:
    for grau, desc in enf["graus"].items():
        session.add(Enfermidade(
            enfermidade_id=id_counter,
            nome=enf["nome"],
            descricao=desc,
            gravidade=gravidade_map.get(grau, "Leve")
        ))
        id_counter += 1
session.commit()

# Inserir pacientes
for i in range(1, 301):
    nascimento = fake.date_of_birth(minimum_age=0, maximum_age=90)
    idade = datetime.now().year - nascimento.year
    faixa = "Criança" if idade <= 10 else "Idoso" if idade >= 60 else "Outros"
    session.add(Paciente(
        paciente_id=i,
        nome=fake.name(),
        data_nascimento=nascimento,
        sexo=random.choice(['M', 'F']),
        cidade_id=random.randint(1, 10),
        faixa_etaria=faixa
    ))
session.commit()

# Inserir tratamentos
total_enfermidades = id_counter - 1
tratamento_id = 1
for enf_id in range(1, total_enfermidades + 1):
    for _ in range(random.randint(20, 25)):
        paciente_id = random.randint(1, 300)
        cidade_id = random.randint(1, 10)
        inicio = fake.date_between(start_date=date(2023, 1, 1), end_date=date(2024, 12, 31))
        duracao = random.randint(5, 60)
        fim = inicio + timedelta(days=duracao)
        custo = round(random.uniform(150, 10000), 2)
        session.add(Tratamento(
            tratamento_id=tratamento_id,
            paciente_id=paciente_id,
            enfermidade_id=enf_id,
            data_inicio=inicio,
            data_fim=fim,
            custo_total=custo,
            cidade_id=cidade_id,
            duracao_dias=duracao
        ))
        tratamento_id += 1

session.commit()
session.close()
