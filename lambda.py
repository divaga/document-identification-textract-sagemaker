import json
import boto3
import base64
import time

def argmax(array):
  index, value = 0, array[0]
  for i,v in enumerate(array):
    if v > value:
      index, value = i,v
  return index

def lambda_handler(event, context):
    eventBody = json.loads(json.dumps(event))['body']
    imageBase64 = json.loads(eventBody)['Image']
    # Amazon Textract client
    textract = boto3.client('textract')
    start_time = time.time()    
    # Call Amazon Textract
    response = textract.detect_document_text(
        Document={
            'Bytes': base64.b64decode(imageBase64)
        })

    detectedText = ''
    doctype = 'UNKNOWN'

    # Print detected text
    for item in response['Blocks']:
        if item['BlockType'] == 'LINE':
            detectedText += item['Text'] + '|'   
    
    # get doc type from detected text
    # PLEASE CHANGE THIS BASED ON YOUR DOCUMENT CHARACTERISTICS!!
    if (detectedText.lower().find("nik") != -1 and detectedText.lower().find("agama") != -1 and detectedText.lower().find("kewarganegaraan") != -1 and detectedText.lower().find("darah") != -1):
        doctype = "KTP"
    if (detectedText.lower().find("surat izin mengemudi") != -1 and detectedText.lower().find("driving license") != -1 ):
        doctype = "SIM"
    
    # sagemaker
    runtime_sm_client = boto3.client(service_name='sagemaker-runtime')

     # PLEASE CHANGE THIS!
    ENDPOINT_NAME = '<YOUR_SAGEMAKER_ENDPOINT_NAME>'

    
    # get sagemaker prediction
    response = runtime_sm_client.invoke_endpoint(
            EndpointName=ENDPOINT_NAME,
            ContentType='image/jpeg',
            Body=base64.b64decode(imageBase64))
    
    prob = json.loads(response['Body'].read())
    duration = time.time() - start_time
    document_type = ['KK', 'KTP', 'PASPOR','SIM']
    classes = document_type
    
    
    index = argmax(prob)
    #print("Result: label - " + document_type[index] + ", probability - " + str(prob[index]))
                
    result= {
        'document_type':doctype,
        'document_classification':document_type[index],
        'classification_confidence':str(prob[index]),
        'detected_text':detectedText,
        'duration':duration
    }

    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }
