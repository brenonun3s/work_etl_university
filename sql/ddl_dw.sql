-- ===== DIMENSÕES =====

CREATE TABLE dim_data (
    sk_data INTEGER PRIMARY KEY,
    data DATE NOT NULL,
    dia INTEGER,
    mes INTEGER,
    nome_mes VARCHAR(20),
    trimestre INTEGER,
    ano INTEGER,
    dia_semana VARCHAR(20)
);

CREATE TABLE dim_cliente (
    sk_cliente SERIAL PRIMARY KEY,
    customerid INTEGER UNIQUE NOT NULL,
    nome VARCHAR(200),
    tipo VARCHAR(20),
    email VARCHAR(100)
);

CREATE TABLE dim_produto (
    sk_produto SERIAL PRIMARY KEY,
    productid INTEGER UNIQUE NOT NULL,
    nome VARCHAR(200),
    categoria VARCHAR(100),
    subcategoria VARCHAR(100),
    preco_lista NUMERIC(12,2)
);

CREATE TABLE dim_territorio (
    sk_territorio SERIAL PRIMARY KEY,
    territoryid INTEGER UNIQUE NOT NULL,
    nome VARCHAR(100),
    pais VARCHAR(10),
    grupo_regiao VARCHAR(100)
);

CREATE TABLE dim_vendedor (
    sk_vendedor SERIAL PRIMARY KEY,
    businessentityid INTEGER UNIQUE NOT NULL,
    nome VARCHAR(200)
);

CREATE TABLE dim_canal (
    sk_canal SERIAL PRIMARY KEY,
    descricao VARCHAR(50) UNIQUE NOT NULL
);

-- ===== FATO =====

CREATE TABLE fato_vendas (
    sk_venda SERIAL PRIMARY KEY,
    sk_data_pedido INTEGER NOT NULL REFERENCES dim_data(sk_data),
    sk_data_envio INTEGER REFERENCES dim_data(sk_data),
    sk_cliente INTEGER NOT NULL REFERENCES dim_cliente(sk_cliente),
    sk_produto INTEGER NOT NULL REFERENCES dim_produto(sk_produto),
    sk_territorio INTEGER REFERENCES dim_territorio(sk_territorio),
    sk_vendedor INTEGER REFERENCES dim_vendedor(sk_vendedor),
    sk_canal INTEGER NOT NULL REFERENCES dim_canal(sk_canal),
    numero_pedido INTEGER NOT NULL,
    quantidade INTEGER NOT NULL,
    preco_unitario NUMERIC(12,2) NOT NULL,
    desconto_unitario NUMERIC(6,4) DEFAULT 0,
    valor_liquido NUMERIC(14,2) NOT NULL,
    custo_total NUMERIC(14,2)
);

CREATE INDEX idx_fato_data_pedido ON fato_vendas(sk_data_pedido);
CREATE INDEX idx_fato_cliente ON fato_vendas(sk_cliente);
CREATE INDEX idx_fato_produto ON fato_vendas(sk_produto);