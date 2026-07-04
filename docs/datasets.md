# Datasets

Esta documentação registra a origem, a organização local e o procedimento de validação de integridade dos dados brutos usados no projeto.

## POP909

**Descrição:**  
Dataset de músicas pop em representação simbólica (MIDI), contendo 909 músicas anotadas.

**Origem:** 

Repositório oficial: <https://github.com/music-x-lab/POP909-Dataset>

> Versão: 
Git commit: `efa0bce`
Download:
2026-06-27
Arquivo:
POP909.zip

**Artigo:**  
Wang et al. (2020). *POP909: A Pop-song Dataset for Music Arrangement Generation*.

Referência do artigo: <https://arxiv.org/abs/2008.07142>

**Licença:**  
MIT License, conforme a documentação oficial do repositório.

**Localização no projeto:**  
`data/raw/POP909`

**Estrutura**
Cada música possui a seguinte organização:

001/
├── 001.mid
├── beat_audio.txt
├── beat_midi.txt
├── chord_audio.txt
├── chord_midi.txt
├── key_audio.txt
└── versions/
    ├──001-v1.mid
    ...

**Descrição dos arquivos (explicação dada do próprio repositório)**

- `001.mid`: arquivo MIDI da música arranjada. A trilha `MELODY` representa a melodia principal, a trilha `BRIDGE` representa a submelodia e a trilha `PIANO` representa o acompanhamento.
- `beat_audio.txt` / `beat_midi.txt`: informações de batidas extraídas do áudio bruto ou do MIDI bruto. A primeira coluna representa o tempo, em segundos, e a segunda coluna representa a ordem da batida.
- `chord_audio.txt` / `chord_midi.txt`: informações de acordes extraídas do áudio bruto ou do MIDI bruto. A primeira e a segunda colunas representam, respectivamente, o tempo de início e o tempo de fim, em segundos, e a terceira coluna representa o nome do acorde.
- `key_audio.txt`: informações de mudança de tonalidade extraídas do áudio bruto. A primeira e a segunda colunas representam, respectivamente, o tempo de início e o tempo de fim, em segundos, e a terceira coluna representa a mudança de tonalidade.
- `versions/`: contém diferentes versões da mesma música arranjada.

**Arquivos utilizados neste projeto**

| Arquivo | Utilização |
|---------|------------|
| *.mid | Sim |
| beat_audio.txt | Possivelmente  |
| beat_midi.txt | Possivelmente |
| chord_audio.txt | Possivelmente |
| chord_midi.txt | Possivelmente |
| key_audio.txt | Possivelmente |
| versions/ | Não |

## Integridade dos dados brutos

Para facilitar a validação reprodutível dos dados, este projeto registra:

- `data/raw/POP909.manifest`
- `data/raw/POP909.sha256`
- `data/raw/zips/POP909.zip.sha256`

O manifesto contém o hash SHA256 de cada arquivo extraído do diretório `POP909`, ordenado pelo caminho relativo. O arquivo `POP909.sha256` registra o hash SHA256 do manifesto. O arquivo `POP909.zip.sha256` registra o hash SHA256 do arquivo ZIP original baixado do repositório oficial.

### Como gerar o manifesto

```powershell
$root = (Resolve-Path "POP909").Path

Get-ChildItem $root -Recurse -File |
    Sort-Object FullName |
    ForEach-Object {
        $relative = $_.FullName.Substring($root.Length + 1).Replace('\','/')
        $hash = (Get-FileHash $_.FullName -Algorithm SHA256).Hash
        "$hash  $relative"
    } |
    Set-Content "POP909.manifest" -Encoding utf8
```

### Como gerar o hash do manifesto

```powershell
$hash = (Get-FileHash "POP909.manifest" -Algorithm SHA256).Hash
"$hash  POP909.manifest" | Set-Content "POP909.sha256"
```

### Como gerar o hash do ZIP

```powershell
$hash = (Get-FileHash "POP909.zip" -Algorithm SHA256).Hash
"$hash  POP909.zip" | Set-Content "POP909.zip.sha256"
```

## Como validar a integridade

1. Baixe o ZIP do dataset a partir da origem oficial.
2. Calcule o hash do arquivo ZIP e compare com `data/raw/zips/POP909.zip.sha256`.
3. Extraia o conteúdo do ZIP para `data/raw/POP909`.
4. Recrie o manifesto a partir dos arquivos extraídos.
5. Calcule o hash do manifesto gerado e compare com `data/raw/POP909.sha256`.
6. Se desejar uma validação arquivo a arquivo, compare o manifesto gerado com `data/raw/POP909.manifest`.

### Exemplo de verificação

```powershell
$expectedZipHash = (Get-Content "data/raw/zips/POP909.zip.sha256").Split(" ")[0]
$currentZipHash = (Get-FileHash "data/raw/zips/POP909.zip" -Algorithm SHA256).Hash
$currentZipHash -eq $expectedZipHash

$expectedManifestHash = (Get-Content "data/raw/POP909.sha256").Split(" ")[0]
$currentManifestHash = (Get-FileHash "data/raw/POP909.manifest" -Algorithm SHA256).Hash
$currentManifestHash -eq $expectedManifestHash
```

Se os comandos retornarem `True`, os hashes principais conferem com os arquivos versionados no repositório.
