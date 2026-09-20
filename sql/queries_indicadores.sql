-- 1. Receita total por período (ano/trimestre)
SELECT d.ano, d.trimestre, SUM(f.valor_liquido) AS receita_total
FROM fato_vendas f
JOIN dim_data d ON d.sk_data = f.sk_data_pedido
GROUP BY d.ano, d.trimestre
ORDER BY d.ano, d.trimestre;

-- 2. Ticket médio
SELECT d.ano, SUM(f.valor_liquido) / COUNT(DISTINCT f.numero_pedido) AS ticket_medio
FROM fato_vendas f
JOIN dim_data d ON d.sk_data = f.sk_data_pedido
GROUP BY d.ano
ORDER BY d.ano;

-- 3. Margem bruta (%)
SELECT d.ano,
       SUM(f.valor_liquido - f.custo_total) / NULLIF(SUM(f.valor_liquido), 0) AS margem_bruta
FROM fato_vendas f
JOIN dim_data d ON d.sk_data = f.sk_data_pedido
GROUP BY d.ano
ORDER BY d.ano;

-- 4. Top 10 produtos por receita
SELECT p.nome, p.categoria, p.subcategoria, SUM(f.valor_liquido) AS receita
FROM fato_vendas f
JOIN dim_produto p ON p.sk_produto = f.sk_produto
GROUP BY p.nome, p.categoria, p.subcategoria
ORDER BY receita DESC
LIMIT 10;

-- 5. Vendas por território
SELECT t.nome, t.pais, SUM(f.valor_liquido) AS receita
FROM fato_vendas f
JOIN dim_territorio t ON t.sk_territorio = f.sk_territorio
GROUP BY t.nome, t.pais
ORDER BY receita DESC;

-- 6. Vendas por canal
SELECT c.descricao AS canal, SUM(f.valor_liquido) AS receita,
       COUNT(DISTINCT f.numero_pedido) AS qtd_pedidos
FROM fato_vendas f
JOIN dim_canal c ON c.sk_canal = f.sk_canal
GROUP BY c.descricao;

-- 7. Crescimento de receita ano a ano (%)
WITH receita_ano AS (
    SELECT d.ano, SUM(f.valor_liquido) AS receita
    FROM fato_vendas f
    JOIN dim_data d ON d.sk_data = f.sk_data_pedido
    GROUP BY d.ano
)
SELECT ano, receita,
       (receita - LAG(receita) OVER (ORDER BY ano)) / NULLIF(LAG(receita) OVER (ORDER BY ano), 0) AS crescimento_yoy
FROM receita_ano
ORDER BY ano;

-- 8. Taxa de recompra (% de clientes com mais de 1 pedido)
WITH pedidos_por_cliente AS (
    SELECT sk_cliente, COUNT(DISTINCT numero_pedido) AS qtd_pedidos
    FROM fato_vendas
    GROUP BY sk_cliente
)
SELECT
    COUNT(*) FILTER (WHERE qtd_pedidos > 1)::numeric / COUNT(*) AS taxa_recompra
FROM pedidos_por_cliente;

-- 9. Prazo médio pedido → envio (em dias)
SELECT AVG(env.data - ped.data) AS prazo_medio_dias
FROM fato_vendas f
JOIN dim_data ped ON ped.sk_data = f.sk_data_pedido
JOIN dim_data env ON env.sk_data = f.sk_data_envio
WHERE f.sk_data_envio IS NOT NULL;

-- 10. Desconto médio aplicado (%)
SELECT d.ano, AVG(f.desconto_unitario) AS desconto_medio
FROM fato_vendas f
JOIN dim_data d ON d.sk_data = f.sk_data_pedido
GROUP BY d.ano
ORDER BY d.ano;