import json
import boto3
from datetime import datetime

dynamodb = boto3.resource('dynamodb',
           region_name='ap-south-1')


def lambda_handler(event, context):
    try:
        params    = event.get(
                   'queryStringParameters') or {}
        device_id = params.get(
                   'device_id', 'mosaic-node-01')

        pol_table = dynamodb.Table('policies')

        # Get specific node policy
        response  = pol_table.get_item(
            Key={'device_id': device_id})
        policy    = response.get('Item', {
            'device_id': device_id,
            'threshold': '0.60',
            'updated_at': 'never'
        })

        # Get all policies for history
        all_resp  = pol_table.scan()
        all_items = all_resp.get('Items', [])
        all_items.sort(
            key=lambda x: x.get('updated_at', ''),
            reverse=True
        )

        # Get feedback stats
        fb_table  = dynamodb.Table('feedback_history')
        fb_resp   = fb_table.scan()
        feedbacks = fb_resp.get('Items', [])

        fp_count  = sum(1 for f in feedbacks
                       if f.get('is_false_positive')
                       == 'True')
        total_fb  = len(feedbacks)
        fp_rate   = (fp_count / total_fb
                     if total_fb > 0 else 0)

        return respond(200, {
            'current_policy':    policy,
            'all_policies':      all_items,
            'feedback_summary': {
                'total_feedbacks':    total_fb,
                'false_positives':    fp_count,
                'false_positive_rate':round(fp_rate, 3)
            },
            'retrieved_at': datetime.utcnow(
                            ).isoformat()
        })

    except Exception as e:
        print(f"Lambda 5 error: {e}")
        return respond(500, {'error': str(e)})


def respond(code, body):
    return {
        'statusCode': code,
        'headers': {
            'Access-Control-Allow-Origin':  '*',
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Methods': '*',
            'Content-Type': 'application/json'
        },
        'body': json.dumps(body)
    }