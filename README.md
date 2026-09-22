# DW AdventureWorks — ETL & Data Warehouse

Data Warehouse e pipeline de ETL construídos a partir da base transacional AdventureWorks, com modelagem dimensional em esquema estrela e carga automatizada em Python.

Data Warehouse and ETL pipeline built from the AdventureWorks transactional database, with a star schema dimensional model and automated loading in Python.

## Stack

- **Fonte / Source:** AdventureWorks (OLTP) → PostgreSQL
- **ETL:** Python (pandas + SQLAlchemy)
- **Data Warehouse:** PostgreSQL, esquema estrela / star schema
- **Dashboard:** Power BI

## Estrutura / Structure

```
sql/    → DDL do DW e queries dos 10 indicadores / DW DDL and the 10 indicator queries
etl/    → script de carga / ETL script
docs/   → diagrama e dicionário de dados / model diagram and data dictionary
```

## Modelo dimensional / Dimensional model

```
                    dim_data
                       |
dim_cliente ---- fato_vendas ---- dim_produto
                       |
              dim_territorio   dim_vendedor
                       |
                   dim_canal
```

Fato no grão de linha de pedido, com 6 dimensões ao redor.
Fact table at order-line grain, surrounded by 6 dimensions.

## Como rodar / How to run

```bash
docker compose up                      # sobe o Postgres com a base fonte / spins up Postgres with the source data
python etl/etl_carga.py                # roda o ETL / runs the ETL
psql -f sql/queries_indicadores.sql    # roda os indicadores / runs the indicators
```

## Autor / Author

Breno Nunes dos Santos — trabalho acadêmico / academic project (Unisales, 2026)
