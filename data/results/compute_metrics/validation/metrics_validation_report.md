# Relatório de Validação das Métricas

Data: 2026-07-07 18:57:52

Tempo de execução: 0.806 segundos

## Resumo

- Total de testes: 46
- Testes aprovados: 46
- Testes reprovados: 0
- Percentual de sucesso: 100.00%

## Resultados

| Métrica testada | Caso de teste | Resultado obtido | Resultado esperado | Status | Mensagem de erro |
| --- | --- | --- | --- | --- | --- |
| global_simple_average | metricas identicas | 1.000000 | similaridade máxima | PASS | - |
| global_simple_average | metricas diferentes | 0.437500 | similaridade intermediaria | PASS | - |
| global_weighted_average | pesos validos | 0.637500 | similaridade ponderada calculada corretamente | PASS | - |
| global_weighted_average | pesos ausentes | PASS | ValueError | PASS | - |
| global_weighted_average | pesos negativos | PASS | ValueError | PASS | - |
| global_weighted_average | soma dos pesos invalida | PASS | ValueError | PASS | - |
| harmony_chord_ngram_similarity | progressões iguais | 1.000000 | similaridade máxima | PASS | - |
| harmony_chord_ngram_similarity | substituicao simples | 0.333333 | similaridade alta | PASS | - |
| harmony_chord_ngram_similarity | sequencia vazia | 1.000000 | similaridade máxima | PASS | - |
| harmony_chord_ngram_similarity | parametro n invalido | PASS | ValueError | PASS | - |
| harmony_harmonic_edit_distance | progressões iguais | 1.000000 | similaridade máxima | PASS | - |
| harmony_harmonic_edit_distance | reharmonizacao | 0.000000 | similaridade intermediaria | PASS | - |
| harmony_harmonic_edit_distance | sequencia vazia | 1.000000 | similaridade máxima | PASS | - |
| harmony_pitch_class_similarity | progressões iguais | 1.000000 | similaridade máxima | PASS | - |
| harmony_pitch_class_similarity | substituicao simples | 0.750000 | similaridade alta | PASS | - |
| harmony_pitch_class_similarity | sequencia completamente diferente | 0.000000 | similaridade baixa | PASS | - |
| harmony_pitch_class_similarity | sequencia vazia | 1.000000 | similaridade máxima | PASS | - |
| melody_interval_ngram_similarity | sequencias identicas | 1.000000 | similaridade próxima de 1 | PASS | - |
| melody_interval_ngram_similarity | sequencias identicas | 1.000000 | similaridade próxima de 1 | PASS | - |
| melody_interval_ngram_similarity | transposicao simples | 1.000000 | similaridade alta | PASS | - |
| melody_interval_ngram_similarity | alteracao de poucos intervalos | 0.333333 | similaridade intermediaria | PASS | - |
| melody_interval_ngram_similarity | sequencias completamente diferentes | 0.000000 | similaridade baixa | PASS | - |
| melody_interval_ngram_similarity | sequencias vazias | 1.000000 | similaridade máxima | PASS | - |
| melody_interval_ngram_similarity | parametro n invalido | PASS | ValueError | PASS | - |
| melody_longest_common_subsequence | sequencias identicas | 1.000000 | similaridade máxima | PASS | - |
| melody_longest_common_subsequence | transposicao simples | 1.000000 | similaridade máxima | PASS | - |
| melody_longest_common_subsequence | sequencias totalmente diferentes | 0.000000 | similaridade baixa | PASS | - |
| melody_longest_common_subsequence | sequencias vazias | 1.000000 | similaridade máxima | PASS | - |
| melody_edit_distance | sequencias identicas | 1.000000 | similaridade máxima | PASS | - |
| melody_edit_distance | transposicao simples | 1.000000 | similaridade máxima | PASS | - |
| melody_edit_distance | sequencias diferentes | 0.000000 | similaridade baixa | PASS | - |
| melody_edit_distance | sequencias vazias | 1.000000 | similaridade máxima | PASS | - |
| rhythm_rhythm_ngram_similarity | padrao identico | 1.000000 | similaridade máxima | PASS | - |
| rhythm_rhythm_ngram_similarity | alteracao de andamento | 1.000000 | similaridade alta | PASS | - |
| rhythm_rhythm_ngram_similarity | alteracao parcial | 0.000000 | similaridade intermediaria | PASS | - |
| rhythm_rhythm_ngram_similarity | padrao completamente diferente | 0.000000 | similaridade baixa | PASS | - |
| rhythm_rhythm_ngram_similarity | sequencia vazia | 1.000000 | similaridade máxima | PASS | - |
| rhythm_rhythm_ngram_similarity | parametro n invalido | PASS | ValueError | PASS | - |
| rhythm_ioi_similarity | padrao identico | 1.000000 | similaridade máxima | PASS | - |
| rhythm_ioi_similarity | alteracao de andamento | 1.000000 | similaridade alta | PASS | - |
| rhythm_ioi_similarity | alteracao parcial | 0.716667 | similaridade intermediaria | PASS | - |
| rhythm_ioi_similarity | sequencia vazia | 1.000000 | similaridade máxima | PASS | - |
| rhythm_rhythmic_edit_distance | padrao identico | 1.000000 | similaridade máxima | PASS | - |
| rhythm_rhythmic_edit_distance | alteracao de andamento | 1.000000 | similaridade alta | PASS | - |
| rhythm_rhythmic_edit_distance | alteracao parcial | 0.000000 | similaridade intermediaria | PASS | - |
| rhythm_rhythmic_edit_distance | sequencia vazia | 1.000000 | similaridade máxima | PASS | - |
