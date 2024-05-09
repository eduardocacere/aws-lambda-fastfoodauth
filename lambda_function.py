import json
import os
import boto3


def lambda_handler(event, context):
    # Extract the username and password from the event
    request_body = event['body']

    if isinstance(request_body, str):
        request_body_data = json.loads(request_body)
    else:
        request_body_data = request_body

    document = request_body_data['document']
    email = request_body_data['email']
    password = request_body_data['password']

    cognito_client = boto3.client('cognito-idp')

    try:
        response = cognito_client.initiate_auth(
            ClientId=os.environ['CLIENT_ID'],
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': document,
                'PASSWORD': password
            },
        )

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Authentication successful',
                'id_token': response['AuthenticationResult']['IdToken'],
                'access_token': response['AuthenticationResult']['AccessToken'],
                'refresh_token': response['AuthenticationResult']['RefreshToken']
            })
        }

    except cognito_client.exceptions.InvalidPasswordException as e:
        return {
            'statusCode': 401,
            'body': json.dumps({'error': f'Invalid password. {e}'})
        }
    except cognito_client.exceptions.UserNotFoundException as e:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': f'User not found. {e}'})
        }
    except cognito_client.exceptions.NotAuthorizedException as e:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': f'Not Authorized {e}'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'An error occurred while processing the request. {e}'})
        }
