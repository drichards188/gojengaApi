def lambda_handler(event, context):
    # handle branch
    if event['resource'] == '/user':
        if event['method'] == 'POST':
            return {'resource': 'user POST'}
        elif event['method'] == 'GET':
            return {'resource': 'user GET'}
        elif event['method'] == 'PUT':
            return {'resource': 'user PUT'}
        elif event['method'] == 'DELETE':
            return {'resource': 'user DELETE'}
