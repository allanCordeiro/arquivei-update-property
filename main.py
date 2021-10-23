import json
import math
import apiArquivei
import dbpersist
from datetime import datetime
from config import Config


def get_nfse():
    db = dbpersist.DbNfse()
    manual_nfse = apiArquivei.ManualNfse(
        Config.get_value('api-id'),
        Config.get_value('api-key')
    )

    count = db.get_cursor()
    while True:
        try:
            nfses = manual_nfse.get_manual_nfses(count)
        except Exception as error:
            print(error)
            break
        timestamp = datetime.now()
        dt_creation = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        if nfses['data']:
            persist = []
            for nfse in nfses['data']:
                persist.append((nfse['id'], 0, dt_creation))
            print(f"rodada {count} concluída.")
            count += int(nfses['count'])
        else:
            break

        db.insert_documents(persist)
    db.update_cursor(count)


def get_documents_to_persist():
    db = dbpersist.DbNfse()
    received_nfse = apiArquivei.ReceivedNfse(
        Config.get_value('api-id'),
        Config.get_value('api-key')
    )

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

    operation_status_code = received_nfse.put_manual_status(body)
    if operation_status_code == 200:
        print("\tLote integrado com sucesso")
        return received_nfse.failed
    else:
        raise Exception(f"Erro HTTP {operation_status_code} ao integar lote. Tente novamente")


def validate_failed_docs(failed, docs):
    validated = docs

    for fail in failed:
        for doc in docs:
            if fail in doc:
                validated.remove(doc)

    return validated


def persist_status(nfse_list):
    db = dbpersist.DbNfse()
    for nfse in nfse_list:
        db.update_document(nfse[0])


if __name__ == "__main__":
    print('capturando os dados de nfse')
    get_nfse()

    print('obtendo as notas pendentes de processamento')
    pending_docs = get_documents_to_persist()

    # quantidade de execucoes(ciclos)
    cycles = math.ceil(len(pending_docs)/50)
    counter_cycle = 1
    counter_doc = 0
    failed_doc = []

    for counter_cycle in range(cycles):
        try:
            data = {"data": jsonfy(pending_docs[counter_doc:counter_doc + 50])}
            failed_doc.extend(update_property(json.dumps(data)))

            counter_doc += 50
        except Exception as err:
            print(err)

    docs_to_update = validate_failed_docs(failed_doc, pending_docs)
    persist_status(docs_to_update)
