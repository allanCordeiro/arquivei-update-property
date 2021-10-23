# PUT em Property da API Arquivei

## O que é
-------------
Script que realiza a atualização via API de uma property chamada `isocr`. O objetivo sistêmico é diferenciar por filtro quais documentos serão ou não exportados.
Também realiza a persistência dos dados em um banco SQLite3.

## Como utilizar
-------------
1. Realizar a instalação do pip (`https://pypi.org/project/pip/`)
2. Instalar as dependências: `pip install -r requirements.txt` no terminal na raiz do clone do projeto
3. Criar um arquivo `.env` na raiz do projeto com as configurações a seguir
```
x-api-id=id-das-credenciais-api-arquivei
x-api-key=key-das-credenciais-api-arquivei
```

À partir daí basta executar o arquivo `main.py` sem parâmetros. Os dados mais específicos serão armazenados em `files\logs`

* A base `bkp_localdb.db` é um banco modelo vazio. Ao iniciar a execução do zero, ele criará a instância correta e fará a criação dos dados à partir dali;
* É realizada uma (ou várias) chamadas ao endpoint `v1/nfse/received/manual`;
* Os ids são persistidos no banco de dados;
* Após isso é realizado chamadas com método `PUT` ao endpoint `v1/nfse/received/isocr`, com no máximo 50 documentos por vez no body, inserindo o valor `manual` a esta propriedade;
* A mesma retorna duas listas. Utilizamos a `failed` para ignorar o status de persistência caso algo tenha saído errado;
* As que recebemos na lsita `success` são persistidas como atualizadas e não são mais enviadas para atualização na API.

Ideal para uso em cronjobs.

## Documentação API Arquivei

https://docs.arquivei.com.br/?urls.primaryName=Arquivei%20API#/nfse/

## Lista de pendências
- [X] Persistência em banco de dados
- [X] Guardar histórico de execução em arquivos .log 
- [ ] Possibilitar URL configurável
- [ ] Possibilitar property configurável
- [ ] Possibilitar valor da property configurável
- [ ] Refatoração
