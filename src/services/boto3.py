import boto3

from src.core.config import app_settings

session = boto3.session.Session()
s3 = session.client(
    service_name='s3',
    endpoint_url='https://storage.yandexcloud.net',
    aws_access_key_id=app_settings.aws_access_key_id,
    aws_secret_access_key=app_settings.aws_secret_access_key,
)

# # Создать новый бакет
# s3.create_bucket(Bucket='bucket-name')

# Загрузить объекты в бакет

## Из строки
s3.put_object(
    Bucket=app_settings.bucket,
    Key='py_script.py',
    Body='TEST',
    StorageClass='COLD'
)

# ## Из файла
# s3.upload_file('this_script.py', 'bucket-name', 'py_script.py')
# s3.upload_file('this_script.py', 'bucket-name', 'script/py_script.py')

# # Получить список объектов в бакете
# for key in s3.list_objects(Bucket='bucket-name')['Contents']:
#     print(key['Key'])

# # Удалить несколько объектов
# forDeletion = [{'Key':'object_name'}, {'Key':'script/py_script.py'}]
# response = s3.delete_objects(Bucket='bucket-name', Delete={'Objects': forDeletion})

# Получить объект
get_object_response = s3.get_object(
    Bucket=app_settings.bucket,
    Key='py_script.py'
)
print(get_object_response['Body'].read())
