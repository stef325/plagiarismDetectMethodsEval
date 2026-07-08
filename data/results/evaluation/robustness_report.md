# Relatório de Robustez das Métricas

Data: 2026-07-08 00:46:43

Threshold utilizado: 0.70

## Resumo do experimento

- Pares positivos: 2800
- Pares negativos: 2800
- Métricas avaliadas: 11
- Tempo de execução: 1.156 segundos

## Métricas avaliadas

| Métrica | Threshold | TP | TN | FP | FN | Precision | Recall | F1-score | FNR | Queda média |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| interval_ngram_similarity | 0.70 | 1011 | 2796 | 4 | 1789 | 0.996059 | 0.361071 | 0.530013 | 0.638929 | 0.548446 |
| lcs_similarity | 0.70 | 1339 | 2796 | 4 | 1461 | 0.997022 | 0.478214 | 0.646392 | 0.521786 | 0.492450 |
| edit_distance_similarity | 0.70 | 1336 | 2796 | 4 | 1464 | 0.997015 | 0.477143 | 0.645411 | 0.522857 | 0.493176 |
| chord_ngram_similarity | 0.70 | 257 | 2800 | 0 | 2543 | 1.000000 | 0.091786 | 0.168139 | 0.908214 | 0.723205 |
| harmonic_edit_distance | 0.70 | 1394 | 2800 | 0 | 1406 | 1.000000 | 0.497857 | 0.664759 | 0.502143 | 0.600634 |
| pitch_class_similarity | 0.70 | 1394 | 2800 | 0 | 1406 | 1.000000 | 0.497857 | 0.664759 | 0.502143 | 0.589699 |
| rhythm_ngram_similarity | 0.70 | 200 | 2800 | 0 | 2600 | 1.000000 | 0.071429 | 0.133333 | 0.928571 | 0.928505 |
| ioi_similarity | 0.70 | 1004 | 2800 | 0 | 1796 | 1.000000 | 0.358571 | 0.527865 | 0.641429 | 0.609720 |
| rhythmic_edit_distance | 0.70 | 200 | 2800 | 0 | 2600 | 1.000000 | 0.071429 | 0.133333 | 0.928571 | 0.927151 |
| simple_average | 0.70 | 399 | 2800 | 0 | 2401 | 1.000000 | 0.142500 | 0.249453 | 0.857500 | 0.656998 |
| weighted_average | 0.70 | 779 | 2800 | 0 | 2021 | 1.000000 | 0.278214 | 0.435317 | 0.721786 | 0.633237 |

## Queda média de similaridade por transformação

| Transformação | Categoria | Queda média | Pares considerados |
| --- | --- | --- | --- |
| chord_substitution | Harmonia | 0.782163 | 200 |
| duration_scaling | Ritmo | 0.972835 | 200 |
| harmony_rhythm | Transformacoes combinadas | 0.335315 | 200 |
| interval_modification | Melodia | 0.780633 | 200 |
| melody_harmony | Transformacoes combinadas | 0.118708 | 200 |
| melody_harmony_rhythm | Transformacoes combinadas | 0.335315 | 200 |
| melody_rhythm | Transformacoes combinadas | 0.216607 | 200 |
| ornamentation | Melodia | 0.785272 | 200 |
| partial_rhythm_modification | Ritmo | 0.973396 | 200 |
| reharmonization | Harmonia | 0.769785 | 200 |
| simplification | Melodia | 0.773976 | 400 |
| tempo_change | Ritmo | 0.889152 | 200 |
| transpose | Melodia | 0.660606 | 200 |
| Harmonia | Harmonia | 0.760148 | 600 |
| Melodia | Melodia | 0.761491 | 800 |
| Ritmo | Ritmo | 0.945128 | 600 |
| Transformacoes combinadas | Transformacoes combinadas | 0.251486 | 800 |
