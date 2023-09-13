from google.cloud import storage
from os import path
import importlib
from config import model_name



def test_gsp(request):
    print('successfully deployed function.')
    print('now is the time for Cloud Storage to bring some data')
    
    bucket_name = 'newsnudge'
    blob_name = 'news.tsv'

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob('/data/predict/{}'.format(blob_name))

    print("I'm curious what blob is:", type(blob), blob)

    if blob.exists():
        content = blob.download_as_text()
        print('below is the content: ', content[:1000])


    # 아래에 다른 folder 내 것들도 불러오는 테스트 진행해보기
    print('\n\n now is the time for importing other modules')
    try:
        Model = getattr(importlib.import_module(f"model.{model_name}"), model_name)
        config = getattr(importlib.import_module('config'), f"{model_name}Config")
    except AttributeError:
        print(f"{model_name} not included!")
        exit()    

    print('Hopefully this will be printed:', Model, config)

    print('\n\n how about bring other directories from outer folders?')

    dir = path.join('../checkpoint', model_name)

    print('here is the directory:', dir)