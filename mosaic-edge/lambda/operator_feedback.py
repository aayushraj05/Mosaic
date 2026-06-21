import json
import boto3
from datetime import datetime
from decimal import Decimal

dynamodb   = boto3.resource('dynamodb',
             region_name='ap-south-1')
iot_client = boto3.client('iot-data',
             region_name='ap-south-1')

MIN_THRESHOLD = 0.40
MAX_THRESHOLD = 0.90
ADAPT_FEEDBACKS = 3


def lambda_handler(event, context):
    print("Received:", json.dumps(event))

    try:
        # Parse body — works for both
        # API Gateway and direct invoke
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        elif isinstance(event.get('body'), dict):
            body = event['body']
        else:
            body = event

        print("Parsed body:", json.dumps(body))

        # Get fields — handles both old and new format
        device_id    = body.get('device_id',
                       body.get('drone_id', 'unknown'))
        timestamp    = body.get('timestamp',
                       body.get('detection_id', ''))
        verdict      = body.get('verdict',
                       body.get('operator_verdict', ''))
        confidence   = float(body.get(
                       'original_confidence',
                       body.get('confidence', 0.5)))
        operator_id  = body.get('operator_id',
                       'operator')

        # Validate required fields
        if not device_id or device_id == 'unknown':
            return respond(400, {
                'error': 'device_id is required'
            })
        if not timestamp:
            return respond(400, {
                'error': 'timestamp is required'
            })
        if verdict not in ['confirmed',
                           'false_detection',
                           'false_positive',
                           'needs_more_review']:
            return respond(400, {
                'error': 'verdict must be: confirmed, '
                         'false_detection, '
                         'false_positive, or '
                         'needs_more_review',
                'received': verdict
            })

        # Normalize verdict
        if verdict in ['false_detection',
                       'false_positive']:
            normalized_verdict = 'false_positive'
            is_fp = True
        else:
            normalized_verdict = verdict
            is_fp = False

        feedback_ts = datetime.utcnow().isoformat()

        # Save to feedback_history
        fb_table = dynamodb.Table('feedback_history')
        fb_table.put_item(Item={
            'device_id':            device_id,
            'timestamp':            feedback_ts,
            'detection_timestamp':  timestamp,
            'original_confidence':  str(confidence),
            'verdict':              normalized_verdict,
            'is_false_positive':    str(is_fp),
            'operator_id':          operator_id
        })
        print(f"Feedback saved for {device_id}")

        # Update detection record verdict
        try:
            det_table = dynamodb.Table('detections')
            det_table.update_item(
                Key={
                    'device_id': device_id,
                    'timestamp': timestamp
                },
                UpdateExpression=(
                    'SET operator_verdict = :v, '
                    'resolved = :r, '
                    'resolved_at = :t, '
                    'operator_id = :o'
                ),
                ExpressionAttributeValues={
                    ':v': normalized_verdict,
                    ':r': 'true',
                    ':t': feedback_ts,
                    ':o': operator_id
                }
            )
            print("Detection record updated")
        except Exception as e:
            print(f"Detection update error: {e}")

        # Compute adaptive policy
        new_threshold = compute_policy(device_id)

        # Push policy to all nodes
        push_policy_to_all(new_threshold)

        return respond(200, {
            'message':          'Feedback processed',
            'device_id':        device_id,
            'timestamp':        timestamp,
            'verdict':          normalized_verdict,
            'new_threshold':    new_threshold,
            'policy_pushed_to': [
                'mosaic-node-01',
                'mosaic-node-02',
                'mosaic-node-03',
                'mosaic-node-04'
            ]
        })

    except Exception as e:
        print(f"Lambda 2 error: {e}")
        import traceback
        traceback.print_exc()
        return respond(500, {'error': str(e)})


def compute_policy(device_id):
    try:
        # Get recent feedback from ALL nodes
        fb_table  = dynamodb.Table('feedback_history')
        response  = fb_table.scan(
            FilterExpression=(
                'attribute_exists(verdict)'
            )
        )
        items = response.get('Items', [])

        if len(items) < ADAPT_FEEDBACKS:
            print(f"Only {len(items)} feedbacks — "
                  f"using default threshold 0.60")
            return 0.60

        # Count recent verdicts
        recent = sorted(
            items,
            key=lambda x: x.get('timestamp', ''),
            reverse=True
        )[:20]

        fp_count   = sum(1 for i in recent
                        if i.get('is_false_positive')
                        == 'True')
        conf_count = sum(1 for i in recent
                        if i.get('verdict')
                        == 'confirmed')
        total      = len(recent)

        fp_rate   = fp_count / total
        conf_rate = conf_count / total

        print(f"FP rate: {fp_rate:.2f} "
              f"Confirm rate: {conf_rate:.2f}")

        # Get current threshold
        pol_table = dynamodb.Table('policies')
        response  = pol_table.get_item(
            Key={'device_id': 'mosaic-node-01'})
        current = float(response.get(
            'Item', {}).get('threshold', 0.60))

        # Adapt threshold
        new_threshold = current
        if fp_rate > 0.40:
            new_threshold = min(
                MAX_THRESHOLD,
                current + 0.05)
            print(f"High FP — raising threshold "
                  f"{current} → {new_threshold}")
        elif conf_rate > 0.70:
            new_threshold = max(
                MIN_THRESHOLD,
                current - 0.03)
            print(f"High confirm — lowering threshold "
                  f"{current} → {new_threshold}")
        else:
            print(f"Threshold stable at {current}")

        new_threshold = round(new_threshold, 2)

        # Save updated policy
        pol_table.put_item(Item={
            'device_id':         'global',
            'threshold':         str(new_threshold),
            'fp_rate':           str(round(fp_rate, 3)),
            'confirm_rate':      str(round(conf_rate, 3)),
            'total_feedbacks':   str(total),
            'updated_at':        datetime.utcnow(
                                 ).isoformat()
        })
        for node in ['mosaic-node-01',
                     'mosaic-node-02',
                     'mosaic-node-03',
                     'mosaic-node-04']:
            pol_table.put_item(Item={
                'device_id':    node,
                'threshold':    str(new_threshold),
                'updated_at':   datetime.utcnow(
                                ).isoformat()
            })

        return new_threshold

    except Exception as e:
        print(f"Policy compute error: {e}")
        return 0.60


def push_policy_to_all(threshold):
    nodes = ['mosaic-node-01',
             'mosaic-node-02',
             'mosaic-node-03',
             'mosaic-node-04']

    policy_payload = json.dumps({
        'threshold':         threshold,
        'confidence_weight': 0.50,
        'pose_weight':       0.30,
        'expression_weight': 0.20,
        'command':           'RESCAN',
        'source':            'operator_feedback',
        'timestamp':         datetime.utcnow(
                             ).isoformat()
    })

    for node in nodes:
        try:
            topic = f"mosaic/node/{node}/policy"
            iot_client.publish(
                topic=topic,
                qos=1,
                payload=policy_payload
            )
            print(f"Policy pushed to {node}: "
                  f"threshold={threshold}")
        except Exception as e:
            print(f"Push to {node} failed: {e}")


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