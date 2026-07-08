# Relatório de Consolidação dos Resultados

Data: 2026-07-08 01:18:06

## Resumo do experimento

- Quantidade total de pares: 5600
- Quantidade de experimentos executados: 4
- Tempo de execução: 0.860 segundos

## Tabela de Similaridade

| pair_id | pair_type | transformação | score melódico | score harmônico | score rítmico | score global |
| --- | --- | --- | --- | --- | --- | --- |
| pair_000001 | positive |  |  |  |  |  |
| pair_000002 | positive |  |  |  |  |  |
| pair_000003 | positive |  |  |  |  |  |
| pair_000004 | positive |  |  |  |  |  |
| pair_000005 | positive | chord_substitution |  |  |  |  |
| pair_000006 | positive | duration_scaling |  |  |  |  |
| pair_000007 | positive | interval_modification |  |  |  |  |
| pair_000008 | positive | ornamentation |  |  |  |  |
| pair_000009 | positive | partial_rhythm_modification |  |  |  |  |
| pair_000010 | positive | reharmonization |  |  |  |  |
| pair_000011 | positive | simplification |  |  |  |  |
| pair_000012 | positive | simplification |  |  |  |  |
| pair_000013 | positive | tempo_change |  |  |  |  |
| pair_000014 | positive | transpose |  |  |  |  |
| pair_000015 | positive |  |  |  |  |  |
| pair_000016 | positive |  |  |  |  |  |
| pair_000017 | positive |  |  |  |  |  |
| pair_000018 | positive |  |  |  |  |  |
| pair_000019 | positive | chord_substitution |  |  |  |  |
| pair_000020 | positive | duration_scaling |  |  |  |  |

## Tabela de Robustez

| métrica | Precision | Recall | F1-score | False Negative Rate |
| --- | --- | --- | --- | --- |
| interval_ngram_similarity | 0.996059 | 0.361071 | 0.530013 | 0.638929 |
| lcs_similarity | 0.997022 | 0.478214 | 0.646392 | 0.521786 |
| edit_distance_similarity | 0.997015 | 0.477143 | 0.645411 | 0.522857 |
| chord_ngram_similarity | 1.000000 | 0.091786 | 0.168139 | 0.908214 |
| harmonic_edit_distance | 1.000000 | 0.497857 | 0.664759 | 0.502143 |
| pitch_class_similarity | 1.000000 | 0.497857 | 0.664759 | 0.502143 |
| rhythm_ngram_similarity | 1.000000 | 0.071429 | 0.133333 | 0.928571 |
| ioi_similarity | 1.000000 | 0.358571 | 0.527865 | 0.641429 |
| rhythmic_edit_distance | 1.000000 | 0.071429 | 0.133333 | 0.928571 |
| simple_average | 1.000000 | 0.142500 | 0.249453 | 0.857500 |
| weighted_average | 1.000000 | 0.278214 | 0.435317 | 0.721786 |

## Tabela de Interpretabilidade

| transformação | componente alterado | score melódico | score harmônico | score rítmico | score global | observações |
| --- | --- | --- | --- | --- | --- | --- |
| melody_harmony_rhythm | Combinações | 1.000000 | 0.645113 | 0.333333 | 0.709123 | Maior sensibilidade observada em ritmo. Componente transformado: Harmonia, Melodia, Ritmo. Maior estabilidade em melodia. O componente transformado foi capturado pela familia mais sensivel. A métrica global permaneceu coerente com o componente transformado. |
| melody_harmony | Combinações | 1.000000 | 0.645113 | 1.000000 | 0.875789 | Maior sensibilidade observada em harmonia. Componente transformado: Harmonia, Melodia. Maior estabilidade em melodia. O componente transformado foi capturado pela familia mais sensivel. A métrica global permaneceu coerente com o componente transformado. |
| harmony_rhythm | Combinações | 1.000000 | 0.645113 | 0.333333 | 0.709123 | Maior sensibilidade observada em ritmo. Componente transformado: Harmonia, Ritmo. Maior estabilidade em melodia. O componente transformado foi capturado pela familia mais sensivel. A métrica global permaneceu coerente com o componente transformado. |
| melody_rhythm | Combinações | 1.000000 | 1.000000 | 0.333333 | 0.833333 | Maior sensibilidade observada em ritmo. Componente transformado: Melodia, Ritmo. Maior estabilidade em melodia. O componente transformado foi capturado pela familia mais sensivel. A métrica global ficou acima do componente transformado. |
| chord_substitution | Harmonia | 0.000000 | 0.645113 | 0.000000 | 0.225789 | Maior sensibilidade observada em melodia. Componente transformado: Harmonia. Maior estabilidade em harmonia. A familia mais sensivel não coincidiu exatamente com o componente transformado. A métrica global ficou abaixo do componente transformado. |
| duration_scaling | Ritmo | 0.000000 | 0.000000 | 0.073353 | 0.018338 | Maior sensibilidade observada em melodia. Componente transformado: Ritmo. Maior estabilidade em ritmo. A familia mais sensivel não coincidiu exatamente com o componente transformado. A métrica global ficou abaixo do componente transformado. |
| interval_modification | Melodia | 0.641308 | 0.000000 | 0.000000 | 0.256523 | Maior sensibilidade observada em harmonia. Componente transformado: Melodia. Maior estabilidade em melodia. A familia mais sensivel não coincidiu exatamente com o componente transformado. A métrica global ficou abaixo do componente transformado. |
| ornamentation | Melodia | 0.633013 | 0.000000 | 0.000000 | 0.253205 | Maior sensibilidade observada em harmonia. Componente transformado: Melodia. Maior estabilidade em melodia. A familia mais sensivel não coincidiu exatamente com o componente transformado. A métrica global ficou abaixo do componente transformado. |
| partial_rhythm_modification | Ritmo | 0.000000 | 0.000000 | 0.067195 | 0.016799 | Maior sensibilidade observada em melodia. Componente transformado: Ritmo. Maior estabilidade em ritmo. A familia mais sensivel não coincidiu exatamente com o componente transformado. A métrica global ficou abaixo do componente transformado. |
| reharmonization | Harmonia | 0.000000 | 0.680952 | 0.000000 | 0.238333 | Maior sensibilidade observada em melodia. Componente transformado: Harmonia. Maior estabilidade em harmonia. A familia mais sensivel não coincidiu exatamente com o componente transformado. A métrica global ficou abaixo do componente transformado. |
| simplification | Harmonia | 0.000000 | 0.836309 | 0.000000 | 0.292708 | Maior sensibilidade observada em melodia. Componente transformado: Harmonia. Maior estabilidade em harmonia. A familia mais sensivel não coincidiu exatamente com o componente transformado. A métrica global ficou abaixo do componente transformado. |
| simplification | Melodia | 0.540965 | 0.000000 | 0.000000 | 0.216386 | Maior sensibilidade observada em harmonia. Componente transformado: Melodia. Maior estabilidade em melodia. A familia mais sensivel não coincidiu exatamente com o componente transformado. A métrica global ficou abaixo do componente transformado. |
| tempo_change | Ritmo | 0.000000 | 0.000000 | 0.333333 | 0.083333 | Maior sensibilidade observada em melodia. Componente transformado: Ritmo. Maior estabilidade em ritmo. A familia mais sensivel não coincidiu exatamente com o componente transformado. A métrica global ficou abaixo do componente transformado. |
| transpose | Melodia | 1.000000 | 0.000000 | 0.000000 | 0.400000 | Maior sensibilidade observada em harmonia. Componente transformado: Melodia. Maior estabilidade em melodia. A familia mais sensivel não coincidiu exatamente com o componente transformado. A métrica global ficou abaixo do componente transformado. |
| melody_harmony_rhythm | Combinações | 1.000000 | 0.632710 | 0.333333 | 0.704782 | Maior sensibilidade observada em ritmo. Componente transformado: Harmonia, Melodia, Ritmo. Maior estabilidade em melodia. O componente transformado foi capturado pela familia mais sensivel. A métrica global permaneceu coerente com o componente transformado. |
| melody_harmony | Combinações | 1.000000 | 0.632710 | 1.000000 | 0.871448 | Maior sensibilidade observada em harmonia. Componente transformado: Harmonia, Melodia. Maior estabilidade em melodia. O componente transformado foi capturado pela familia mais sensivel. A métrica global permaneceu coerente com o componente transformado. |
| harmony_rhythm | Combinações | 1.000000 | 0.632710 | 0.333333 | 0.704782 | Maior sensibilidade observada em ritmo. Componente transformado: Harmonia, Ritmo. Maior estabilidade em melodia. O componente transformado foi capturado pela familia mais sensivel. A métrica global permaneceu coerente com o componente transformado. |
| melody_rhythm | Combinações | 1.000000 | 1.000000 | 0.333333 | 0.833333 | Maior sensibilidade observada em ritmo. Componente transformado: Melodia, Ritmo. Maior estabilidade em melodia. O componente transformado foi capturado pela familia mais sensivel. A métrica global ficou acima do componente transformado. |
| chord_substitution | Harmonia | 0.000000 | 0.632710 | 0.000000 | 0.221448 | Maior sensibilidade observada em melodia. Componente transformado: Harmonia. Maior estabilidade em harmonia. A familia mais sensivel não coincidiu exatamente com o componente transformado. A métrica global ficou abaixo do componente transformado. |
| duration_scaling | Ritmo | 0.000000 | 0.000000 | 0.064160 | 0.016040 | Maior sensibilidade observada em melodia. Componente transformado: Ritmo. Maior estabilidade em ritmo. A familia mais sensivel não coincidiu exatamente com o componente transformado. A métrica global permaneceu coerente com o componente transformado. |

## Resumo por experimento

| experimento | quantidade de pares | média melódica | média harmônica | média rítmica | média global |
| --- | --- | --- | --- | --- | --- |
| Outros | 3600 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| Transformações Harmônicas | 400 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| Transformações Melódicas | 1000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| Transformações Rítmicas | 600 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |

## Estatísticas gerais

| família | média | mediana | desvio padrão | mínimo | Q1 | Q3 | máximo |
| --- | --- | --- | --- | --- | --- | --- | --- |
| melody | 0.274688 | 0.040541 | 0.388629 | 0.000000 | 0.000000 | 0.550000 | 1.000000 |
| harmony | 0.188341 | 0.000000 | 0.324852 | 0.000000 | 0.000000 | 0.218954 | 1.000000 |
| rhythm | 0.107296 | 0.000000 | 0.280425 | 0.000000 | 0.000000 | 0.000000 | 1.000000 |
| global | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |

## Principais resultados

- Os resultados consolidados foram agrupados por tipo de transformação.
- A interpretação considera as saídas já produzidas pelos pipelines anteriores.
- As estatísticas gerais usam apenas os resultados existentes.
