import json
import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime

dynamodb  = boto3.resource('dynamodb',
            region_name='ap-south-1')
s3_client = boto3.client('s3',
            region_name='ap-south-1')

S3_BUCKET = 'mosaic-snapshots-aayush'

NODE_IDS = [
    'mosaic-node-01',
    'mosaic-node-02',
    'mosaic-node-03',
    'mosaic-node-04'
]


def lambda_handler(event, context):
    print("Lambda 3 triggered")

    try:
        params    = event.get(
                   'queryStringParameters') or {}
        device_id = params.get('device_id')
        status    = params.get('status')
        priority  = params.get('priority')
        verdict   = params.get('verdict')
        limit     = int(params.get('limit', 50))

        table = dynamodb.Table('detections')
        items = []

        if device_id:
            # Query specific node
            response = table.query(
                KeyConditionExpression=Key(
                    'device_id').eq(device_id),
                ScanIndexForward=False,
                Limit=limit
            )
            items = response.get('Items', [])
            print(f"Node {device_id}: "
                  f"{len(items)} items")

        else:
            # Query EACH node separately
            # Get equal items from each node
            per_node = max(10,
                          limit // len(NODE_IDS))

            for node_id in NODE_IDS:
                try:
                    response = table.query(
                        KeyConditionExpression=Key(
                            'device_id').eq(
                            node_id),
                        ScanIndexForward=False,
                        Limit=per_node
                    )
                    node_items = response.get(
                        'Items', [])
                    items.extend(node_items)
                    print(f"{node_id}: "
                          f"{len(node_items)}"
                          f" items")
                except Exception as e:
                    print(f"{node_id} error: {e}")

        print(f"Total items: {len(items)}")

        # Apply filters
        if status:
            items = [i for i in items
                     if i.get('status') == status]
        if priority:
            items = [i for i in items
                     if i.get('priority') == priority]
        if verdict:
            items = [i for i in items
                     if i.get('operator_verdict')
                     == verdict]

        # Sort by timestamp newest first
        items.sort(
            key=lambda x: x.get('timestamp', ''),
            reverse=True
        )

        # Build response with image URLs
        cleaned = []
        img_count = 0

        for item in items:
            image_url = None
            s3_key    = item.get('s3_image_key')

            if s3_key:
                try:
                    image_url = s3_client\
                        .generate_presigned_url(
                        'get_object',
                        Params={
                            'Bucket': S3_BUCKET,
                            'Key':    s3_key
                        },
                        ExpiresIn=3600
                    )
                    img_count += 1
                except Exception as e:
                    print(f"URL error: {e}")
                    image_url = (
                        f"https://{S3_BUCKET}"
                        f".s3.ap-south-1"
                        f".amazonaws.com/{s3_key}"
                    )

            cleaned.append({
                'device_id':        item.get(
                                    'device_id'),
                'timestamp':        item.get(
                                    'timestamp'),
                'status':           item.get(
                                    'status'),
                'priority':         item.get(
                                    'priority'),
                'confidence':       item.get(
                                    'confidence'),
                'yolo_score':       item.get(
                                    'yolo_score'),
                'pose_score':       item.get(
                                    'pose_score'),
                'expression':       item.get(
                                    'expression'),
                'expression_score': item.get(
                                    'expression_score'),
                'pose_indicators':  item.get(
                                    'pose_indicators'),
                'operator_verdict': item.get(
                                    'operator_verdict'),
                'victim_confirmed': item.get(
                                    'victim_confirmed'),
                'requires_review':  item.get(
                                    'requires_review'),
                'resolved':         item.get(
                                    'resolved'),
                'lat':              item.get('lat'),
                'lon':              item.get('lon'),
                'altitude_m':       item.get(
                                    'altitude_m'),
                'battery_pct':      item.get(
                                    'battery_pct'),
                's3_image_key':     s3_key,
                'image_url':        image_url,
                'simulated':        item.get(
                                    'simulated'),
                'ingested_at':      item.get(
                                    'ingested_at')
            })

        print(f"Returning {len(cleaned)} items")
        print(f"Items with images: {img_count}")

        return respond(200, {
            'count':      len(cleaned),
            'detections': cleaned
        })

    except Exception as e:
        print(f"Lambda 3 error: {e}")
        import traceback
        traceback.print_exc()
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