import json
import math
import logging
import apiArquivei
import dbpersist
from datetime import datetime
from config import Config

'''logging configuration info
'''
log_format = '%(asctime)s:%(levelname)s:%(filename)s:%(message)s'
logging.basicConfig(filename=f"files/logs/persist-{datetime.now().strftime('%Y-%m-%d')}.log",
                    filemode ='a',
                    level=logging.DEBUG,
                    format=log_format
                    )
logger = logging.getLogger('root')


def get_nfse():
    db = dbpersist.DbNfse()
    manual_nfse = apiArquivei.ManualNfse(
        Config.get_value('api-id'),
        Config.get_value('api-key')
    )

    try:
        count = db.get_cursor()
    except Exception as err:
        logger.error(f"Erro ao obter o cursor no banco de dados: {err}")
        raise
    while True:
        try:
            nfses = manual_nfse.get_manual_nfses(count)
        except Exception as error:
            logger.error(f"Excecao durante tentativa de comunicacao com API: {error=}")
            break
        timestamp = datetime.now()
        dt_creation = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        if nfses['data']:
            persist = []
            for nfse in nfses['data']:
                persist.append((nfse['id'], 0, dt_creation))
            logger.info(f"Execucao no cursor {count} concluido")
            count += int(nfses['count'])
        else:
            logger.warning(f"O cursor {count} nao trouxe nenhum dado.")
            raise

        db.insert_documents(persist)
    db.update_cursor(count)


def get_documents_to_persist():
    try:
        db = dbpersist.DbNfse()
    except Exception as err:
        logger.error(f"Erro ao obter os documentos da tabela nfse: {err=}")
        raise

    return db.get_pendent_documents()


def jsonfy(documents):
    data = []
    for document in documents:
        data.append(
            {
                "id": document[1],
                "value": "manual"  # property isocr
            }
        )
    return data


def update_property(body):
    received_nfse = apiArquivei.ReceivedNfse(
        Config.get_value('api-id'),
        Config.get_value('api-key')
    )

    try:
        operation_status_code = received_nfse.put_manual_status(body)
        if operation_status_code == 200:
            return received_nfse.failed
        else:
            raise Exception(f"Erro HTTP {operation_status_code} ao integar lote. Tente novamente")
    except Exception as err:
        logger.error(f"Erro ao realizar chamada PUT: {err=}")
        raise

def validate_failed_docs(failed, docs):
    validated = docs

    for fail in failed:
        for doc in docs:
            if fail in doc:
                validated.remove(doc)

    return validated


def persist_status(nfse_list):
    db = dbpersist.DbNfse()
    try:
        for nfse in nfse_list:
            db.update_document(nfse[0])
    except Exception as err:
        logger.error(f"Erro ao persistir status da tabela nfse: {err=}")


if __name__ == "__main__":
    logger.info('Iniciando chamada a API')
    get_nfse()
    logger.info('Consulta a API finalizada')

    logger.info('Capturando documentos pendentes na tabela')
    pending_docs = get_documents_to_persist()

    # quantidade de execucoes(ciclos)
    cycles = math.ceil(len(pending_docs)/50)
    logger.info(f'Total de ciclos na operacao: {cycles}')
    counter_cycle = 1
    counter_doc = 0
    failed_doc = []

    for counter_cycle in range(cycles):
        try:
            data = {"data": jsonfy(pending_docs[counter_doc:counter_doc + 50])}
            failed_doc.extend(update_property(json.dumps(data)))
            counter_doc += 50
        except Exception as err:
            logger.error(f'Erro ao realizar operacao PUT na API. {err}')

    logger.info(f"Total de ids de nfses que falharam: {len(failed_doc)}")
    if len(failed_doc) > 0:
        logger.info(f"Lista: {failed_doc}")
    docs_to_update = validate_failed_docs(failed_doc, pending_docs)
    logger.info('Persistindo status no banco de dados')
    persist_status(docs_to_update)
    logger.info('Operacao finalizada')