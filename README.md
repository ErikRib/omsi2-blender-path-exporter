# OMSI 2 Path / PassengerCabin Exporter

Addon para **Blender 2.79** que facilita a criacao de path points e posicoes de passageiros para mods do **OMSI 2**.

Desenvolvido por **Japa Games** (Erik Ribeiro).

---

## Instalacao

1. Baixe o arquivo 
2. No Blender 2.79: **File > User Preferences > Add-ons**
3. Clique em **Install Add-on from File** e selecione o 
4. Pesquise **OMSI 2** na lista e ative o addon
5. Clique em **Save User Settings**

O painel aparece em: **View3D > Tool Shelf (T) > aba OMSI 2**

---

## Funcionalidades

### Path Points ()

Crie objetos Empty nomeados , , ... posicionados dentro do onibus no Blender.

| Custom Property | Funcao |
|---|---|
|  | Indices dos pontos ligados (ex: ) ->  |
|  | Igual, mas gera  |
|  | Insere  antes dos links |

### Passenger Cabin ()

Crie objetos Empty nomeados , ...

| Custom Property | Funcao |
|---|---|
|  | Altura do assento ( = em pe,  = sentado) |
|  | Rotacao em graus ( = frente,  = costas) |

### Nomes especiais

| Nome do objeto | Gera no CFG |
|---|---|
|  |  (posicao do motorista) |
|  |  (custom prop  = indice) |
|  |  (custom prop  = indice) |
|  |  (articulado frente->tras) |
|  |  (articulado tras->frente) |
|  |  (catraca) |

---

## Fluxo de trabalho

1. Posicione o cursor 3D onde quer o ponto
2. Clique **Adicionar PATH_N** ou **Adicionar PASSPOS_N** no painel
3. Com o objeto selecionado, defina os links e propriedades no painel
4. Clique **Exportar Path CFG** / **Exportar PassengerCabin CFG**

---

## Compatibilidade

- Blender 2.79
- OMSI 2 (formato  de veiculos articulados e simples)

---

## Licenca

MIT License - livre para usar, modificar e redistribuir com creditos.
