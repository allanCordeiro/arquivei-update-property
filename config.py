from decouple import config, UndefinedValueError


class Config:
    @staticmethod
    def get_value(data):
        try:
            if data == 'account-id':
                return config('account-id')
            elif data == 'api-id':
                return config('x-api-id')
            elif data == 'api-key':
                return config('x-api-key')
            else:
                raise UndefinedValueError('chave nao reconhecida')
        except:
            raise UndefinedValueError('chave invalida ou arquivo .env inexistente')
