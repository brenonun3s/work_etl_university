import pandas as pd
from sqlalchemy import create_engine, text

SRC = create_engine("postgresql+psycopg2://postgres:postgres@localhost:5432/Adventureworks")
DW = create_engine("postgresql+psycopg2://postgres:postgres@localhost:5432/dw_adventureworks")


def carregar_dim_canal():
    df = pd.DataFrame({
        "sk_canal": [1, 2],
        "descricao": ["Internet", "Revenda"],
    })
    df.to_sql("dim_canal", DW, if_exists="append", index=False)
    print(f"dim_canal: {len(df)} linhas")


def carregar_dim_territorio():
    df = pd.read_sql("""
        SELECT territoryid, name AS nome, countryregioncode AS pais, "group" AS grupo_regiao
        FROM sales.salesterritory
    """, SRC)
    df.insert(0, "sk_territorio", range(1, len(df) + 1))
    df = pd.concat([df, pd.DataFrame([{
        "sk_territorio": 0, "territoryid": -1, "nome": "Não informado",
        "pais": None, "grupo_regiao": None,
    }])], ignore_index=True)
    df.to_sql("dim_territorio", DW, if_exists="append", index=False)
    print(f"dim_territorio: {len(df)} linhas")
    return df.set_index("territoryid")["sk_territorio"].to_dict()


def carregar_dim_vendedor():
    df = pd.read_sql("""
        SELECT sp.businessentityid,
               p.firstname || ' ' || p.lastname AS nome
        FROM sales.salesperson sp
        JOIN person.person p ON p.businessentityid = sp.businessentityid
    """, SRC)
    df.insert(0, "sk_vendedor", range(1, len(df) + 1))
    df = pd.concat([df, pd.DataFrame([{
        "sk_vendedor": 0, "businessentityid": -1, "nome": "Não informado",
    }])], ignore_index=True)
    df.to_sql("dim_vendedor", DW, if_exists="append", index=False)
    print(f"dim_vendedor: {len(df)} linhas")
    return df.set_index("businessentityid")["sk_vendedor"].to_dict()


def carregar_dim_cliente():
    df = pd.read_sql("""
        SELECT c.customerid,
               COALESCE(p.firstname || ' ' || p.lastname, st.name) AS nome,
               CASE WHEN c.personid IS NOT NULL THEN 'Pessoa Física' ELSE 'Loja' END AS tipo
        FROM sales.customer c
        LEFT JOIN person.person p ON p.businessentityid = c.personid
        LEFT JOIN sales.store st ON st.businessentityid = c.storeid
    """, SRC)
    df.insert(0, "sk_cliente", range(1, len(df) + 1))
    df["email"] = None
    df.to_sql("dim_cliente", DW, if_exists="append", index=False)
    print(f"dim_cliente: {len(df)} linhas")
    return df.set_index("customerid")["sk_cliente"].to_dict()


def carregar_dim_produto():
    df = pd.read_sql("""
        SELECT pr.productid, pr.name AS nome,
               pc.name AS categoria, ps.name AS subcategoria,
               pr.listprice AS preco_lista
        FROM production.product pr
        LEFT JOIN production.productsubcategory ps ON ps.productsubcategoryid = pr.productsubcategoryid
        LEFT JOIN production.productcategory pc ON pc.productcategoryid = ps.productcategoryid
    """, SRC)
    df.insert(0, "sk_produto", range(1, len(df) + 1))
    df.to_sql("dim_produto", DW, if_exists="append", index=False)
    print(f"dim_produto: {len(df)} linhas")
    return df.set_index("productid")["sk_produto"].to_dict()


def carregar_dim_data(datas):
    datas = pd.to_datetime(pd.Series(datas).dropna().unique())
    df = pd.DataFrame({"data": datas})
    df["sk_data"] = df["data"].dt.strftime("%Y%m%d").astype(int)
    df["dia"] = df["data"].dt.day
    df["mes"] = df["data"].dt.month
    df["nome_mes"] = df["data"].dt.month_name()
    df["trimestre"] = df["data"].dt.quarter
    df["ano"] = df["data"].dt.year
    df["dia_semana"] = df["data"].dt.day_name()
    df = df.drop_duplicates(subset="sk_data")[
        ["sk_data", "data", "dia", "mes", "nome_mes", "trimestre", "ano", "dia_semana"]
    ]
    df.to_sql("dim_data", DW, if_exists="append", index=False)
    print(f"dim_data: {len(df)} linhas")


def carregar_fato(map_territorio, map_vendedor, map_cliente, map_produto):
    df = pd.read_sql("""
        SELECT h.salesorderid, h.orderdate, h.shipdate, h.customerid,
               h.territoryid, h.salespersonid, h.onlineorderflag,
               d.productid, d.orderqty, d.unitprice, d.unitpricediscount,
               (d.unitprice * (1 - d.unitpricediscount) * d.orderqty) AS linetotal,
               p.standardcost
        FROM sales.salesorderheader h
        JOIN sales.salesorderdetail d ON d.salesorderid = h.salesorderid
        JOIN production.product p ON p.productid = d.productid
    """, SRC)

    df["sk_data_pedido"] = pd.to_datetime(df["orderdate"]).dt.strftime("%Y%m%d").astype(int)
    df["sk_data_envio"] = pd.to_datetime(df["shipdate"]).dt.strftime("%Y%m%d")
    df["sk_data_envio"] = df["sk_data_envio"].where(df["shipdate"].notna(), None)
    df["sk_data_envio"] = df["sk_data_envio"].astype("Int64")

    df["sk_cliente"] = df["customerid"].map(map_cliente)
    df["sk_produto"] = df["productid"].map(map_produto)
    df["sk_territorio"] = df["territoryid"].map(map_territorio).fillna(0).astype(int)
    df["sk_vendedor"] = df["salespersonid"].map(map_vendedor).fillna(0).astype(int)
    df["sk_canal"] = df["onlineorderflag"].map({True: 1, False: 2})

    df["custo_total"] = df["orderqty"] * df["standardcost"]

    fato = df.rename(columns={
        "salesorderid": "numero_pedido", "orderqty": "quantidade",
        "unitprice": "preco_unitario", "unitpricediscount": "desconto_unitario",
        "linetotal": "valor_liquido",
    })[[
        "sk_data_pedido", "sk_data_envio", "sk_cliente", "sk_produto",
        "sk_territorio", "sk_vendedor", "sk_canal", "numero_pedido",
        "quantidade", "preco_unitario", "desconto_unitario", "valor_liquido", "custo_total",
    ]]

    fato.to_sql("fato_vendas", DW, if_exists="append", index=False)
    print(f"fato_vendas: {len(fato)} linhas")
    return df


if __name__ == "__main__":
    territorio_df = pd.read_sql("""
        SELECT territoryid, name AS nome FROM sales.salesterritory
    """, SRC)
    territorio_df.insert(0, "sk_territorio", range(1, len(territorio_df) + 1))
    map_territorio = territorio_df.set_index("territoryid")["sk_territorio"].to_dict()
    map_territorio[-1] = 0

    vendedor_df = pd.read_sql("""
        SELECT sp.businessentityid FROM sales.salesperson sp
    """, SRC)
    vendedor_df.insert(0, "sk_vendedor", range(1, len(vendedor_df) + 1))
    map_vendedor = vendedor_df.set_index("businessentityid")["sk_vendedor"].to_dict()
    map_vendedor[-1] = 0

    cliente_df = pd.read_sql("SELECT customerid FROM sales.customer", SRC)
    cliente_df.insert(0, "sk_cliente", range(1, len(cliente_df) + 1))
    map_cliente = cliente_df.set_index("customerid")["sk_cliente"].to_dict()

    produto_df = pd.read_sql("SELECT productid FROM production.product", SRC)
    produto_df.insert(0, "sk_produto", range(1, len(produto_df) + 1))
    map_produto = produto_df.set_index("productid")["sk_produto"].to_dict()

    carregar_fato(map_territorio, map_vendedor, map_cliente, map_produto)

    from sqlalchemy import text
    with DW.connect() as conn:
        conn.execute(text("SELECT setval('dim_territorio_sk_territorio_seq', (SELECT MAX(sk_territorio) FROM dim_territorio))"))
        conn.execute(text("SELECT setval('dim_vendedor_sk_vendedor_seq', (SELECT MAX(sk_vendedor) FROM dim_vendedor))"))
        conn.execute(text("SELECT setval('dim_cliente_sk_cliente_seq', (SELECT MAX(sk_cliente) FROM dim_cliente))"))
        conn.execute(text("SELECT setval('dim_produto_sk_produto_seq', (SELECT MAX(sk_produto) FROM dim_produto))"))
        conn.commit()

    print("ETL concluído.")