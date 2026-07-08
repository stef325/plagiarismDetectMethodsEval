# Relatório de Interpretabilidade das Métricas

Data: 2026-07-08 01:04:22

## Resumo da avaliação

- Pares positivos: 2800
- Pares negativos: 2800
- Categorias de transformação: 4
- Tempo de execução: 308.281 segundos

## Estatísticas por tipo de transformação

| Categoria | Pares | Média alvo | Mediana alvo | DP alvo | Mín alvo | Máx alvo | Média global | Mediana global | DP global | Mín global | Máx global | Média da diferença |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Combinações | 800 | 0.745139 | 0.687082 | 0.093441 | 0.466667 | 0.906173 | 0.782266 | 0.734815 | 0.075384 | 0.506667 | 0.901481 | 0.587994 |
| Harmonia | 600 | 0.711231 | 0.687976 | 0.096628 | 0.066667 | 1.000000 | 0.250931 | 0.240875 | 0.032529 | 0.209649 | 0.438889 | 0.715824 |
| Melodia | 800 | 0.702749 | 0.638888 | 0.184679 | 0.222222 | 1.000000 | 0.281100 | 0.255555 | 0.073871 | 0.088889 | 0.400000 | 0.702749 |
| Ritmo | 600 | 0.163236 | 0.091081 | 0.124827 | 0.000000 | 0.365365 | 0.042809 | 0.023185 | 0.041445 | 0.003512 | 0.483333 | 0.167681 |

## Comparação entre métricas individuais e métrica global

| Categoria | Melodia | Harmonia | Ritmo | Média simples | Média ponderada |
| --- | --- | --- | --- | --- | --- |
| Combinações | 1.000000 | 0.734116 | 0.501301 | 0.745139 | 0.782266 |
| Harmonia | 0.005000 | 0.711231 | 0.000000 | 0.238744 | 0.250931 |
| Melodia | 0.702749 | 0.000000 | 0.000000 | 0.234250 | 0.281100 |
| Ritmo | 0.005000 | 0.000000 | 0.163236 | 0.056079 | 0.042809 |

## Evidências interpretativas

### Combinações

- Métrica mais sensível: Ritmo
- Métrica mais estável: Melodia
- Maior variação: Ritmo
- Comportamento da métrica global: A métrica global acompanhou de perto o componente transformado.

### Harmonia

- Métrica mais sensível: Ritmo
- Métrica mais estável: Harmonia
- Maior variação: Harmonia
- Comportamento da métrica global: A métrica global refletiu uma queda mais forte que o componente transformado.

### Melodia

- Métrica mais sensível: Harmonia
- Métrica mais estável: Melodia
- Maior variação: Melodia
- Comportamento da métrica global: A métrica global refletiu uma queda mais forte que o componente transformado.

### Ritmo

- Métrica mais sensível: Harmonia
- Métrica mais estável: Ritmo
- Maior variação: Ritmo
- Comportamento da métrica global: A métrica global refletiu uma queda mais forte que o componente transformado.

