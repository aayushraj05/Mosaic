import json
import boto3
from datetime import datetime
import base64

dynamodb  = boto3.resource('dynamodb',
            region_name='ap-south-1')
s3_client = boto3.client('s3',
            region_name='ap-south-1')

# UPDATE THIS TO YOUR EXACT BUCKET NAME
S3_BUCKET = 'mosaic-snapshots-aayush'


def lambda_handler(event, context):
    print("Lambda 1 triggered")
    print("Event:", json.dumps(event))

    try:
        # Handle both drone_id and device_id
        device_id = (event.get('device_id') or
                     event.get('drone_id') or
                     'unknown')
        timestamp = (event.get('timestamp') or
                     datetime.utcnow().isoformat())
        detection = event.get('detection')
        simulated = event.get('simulated', False)

        print(f"Device: {device_id}")
        print(f"Has detection: {detection is not None}")

        # Always update swarm_nodes
        update_swarm_node(
            event, device_id, timestamp)
        print("Swarm node updated")

        # Heartbeat only
        if not detection:
            print(f"Heartbeat from {device_id}")
            return respond(200, {
                'message': 'Heartbeat recorded',
                'device_id': device_id
            })

        status   = detection.get('status', 'unknown')
        priority = detection.get('priority', 'LOW')
        print(f"Status: {status}, Priority: {priority}")

        # Set verdict
        if status == 'confirmed':
            verdict = 'auto-confirmed'
        elif status == 'uncertain':
            verdict = 'pending'
        elif status == 'possible_missed_victim':
            verdict = 'needs_review'
        else:
            verdict = 'unknown'

        # Build item for DynamoDB
        item = {
            'device_id':         device_id,
            'timestamp':         timestamp,
            'simulated':         str(simulated),
            'status':            status,
            'priority':          priority,
            'confidence':        str(detection.get(
                                 'confidence', 0)),
            'yolo_score':        str(detection.get(
                                 'yolo_score', 0)),
            'pose_score':        str(detection.get(
                                 'pose_score', 0)),
            'expression':        str(detection.get(
                                 'expression', 'N/A')),
            'expression_score':  str(detection.get(
                                 'expression_score', 0)),
            'pose_indicators':   json.dumps(
                                 detection.get(
                                 'pose_indicators',
                                 detection.get(
                                 'indicators', []))),
            'victim_confirmed':  str(detection.get(
                                 'victim_confirmed',
                                 False)),
            'requires_review':   str(detection.get(
                                 'requires_review',
                                 False)),
            'threshold_used':    str(detection.get(
                                 'threshold_used',
                                 0.60)),
            'operator_verdict':  verdict,
            'resolved':          str(
                                 status == 'confirmed'),
            'lat':               str(event.get(
                                 'location', {}).get(
                                 'lat', 0)),
            'lon':               str(event.get(
                                 'location', {}).get(
                                 'lon', 0)),
            'altitude_m':        str(event.get(
                                 'flight', {}).get(
                                 'altitude_m', 0)),
            'battery_pct':       str(event.get(
                                 'power', {}).get(
                                 'battery_pct', 0)),
            'ingested_at':       datetime.utcnow(
                                 ).isoformat()
        }

        print("Writing to detections table...")
        det_table = dynamodb.Table('detections')
        det_table.put_item(Item=item)
        print("DynamoDB write OK")

        # S3 upload for uncertain with image
        if (status == 'uncertain' and
                detection.get('image_b64')):
            try:
                print("Uploading image to S3...")
                img_bytes = base64.b64decode(
                    detection['image_b64'])
                s3_key = (f"mosaic/{device_id}/"
                          f"{timestamp}.jpg")
                s3_client.put_object(
                    Bucket=S3_BUCKET,
                    Key=s3_key,
                    Body=img_bytes,
                    ContentType='image/jpeg'
                )
                print(f"S3 upload OK: {s3_key}")
                # Update item with s3 key
                det_table.update_item(
                    Key={
                        'device_id': device_id,
                        'timestamp': timestamp
                    },
                    UpdateExpression=
                        'SET s3_image_key = :k',
                    ExpressionAttributeValues={
                        ':k': s3_key
                    }
                )
            except Exception as e:
                print(f"S3 error: {e}")

        return respond(200, {
            'message':   'Detection processed',
            'device_id': device_id,
            'status':    status,
            'verdict':   verdict
        })

    except Exception as e:
        print(f"LAMBDA ERROR: {e}")
        import traceback
        traceback.print_exc()
        return respond(500, {'error': str(e)})


def update_swarm_node(event,
                      device_id, timestamp):
    try:
        power    = event.get('power', {})
        flight   = event.get('flight', {})
        location = event.get('location', {})
        sensors  = event.get('sensors', {})
        comms    = event.get('comms', {})
        mission  = event.get('mission_stats', {})
        detection= event.get('detection')

        battery = float(
            power.get('battery_pct', 0))
        if battery > 50:
            health = 'GOOD'
        elif battery > 20:
            health = 'LOW'
        elif battery > 5:
            health = 'CRITICAL'
        else:
            health = 'EMPTY'

        det_status = 'scanning'
        if detection:
            det_status = detection.get(
                'status', 'scanning')

        table = dynamodb.Table('swarm_nodes')
        table.put_item(Item={
            'device_id':         device_id,
            'last_seen':         timestamp,
            'status':            flight.get(
                                 'mode', 'ACTIVE'),
            'detection_status':  det_status,
            'battery_pct':       str(battery),
            'battery_health':    health,
            'altitude_m':        str(flight.get(
                                 'altitude_m', 0)),
            'speed_ms':          str(flight.get(
                                 'speed_ms', 0)),
            'heading_deg':       str(flight.get(
                                 'heading_deg', 0)),
            'lat':               str(location.get(
                                 'lat', 0)),
            'lon':               str(location.get(
                                 'lon', 0)),
            'temperature_c':     str(sensors.get(
                                 'temperature_c', 0)),
            'cpu_usage_pct':     str(sensors.get(
                                 'cpu_usage_pct', 0)),
            'ram_used_mb':       str(sensors.get(
                                 'ram_used_mb', 0)),
            'signal_dbm':        str(comms.get(
                                 'signal_dbm', 0)),
            'packet_loss_pct':   str(comms.get(
                                 'packet_loss_pct',
                                 0)),
            'detections_today':  str(mission.get(
                                 'detections_today',
                                 0)),
            'confirmed_victims': str(mission.get(
                                 'confirmed_victims',
                                 0)),
            'simulated':         str(event.get(
                                 'simulated', False)),
            'updated_at':        datetime.utcnow(
                                 ).isoformat()
        })
        print("swarm_nodes updated OK")
    except Exception as e:
        print(f"Swarm node error: {e}")


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

print(f"Writing to table: detections")
print(f"Region: ap-south-1")
print(f"Item device_id: {device_id}")
print(f"Item timestamp: {timestamp}")

det_table = dynamodb.Table('detections')
response = det_table.put_item(Item=item)
print(f"DynamoDB response: {response}")
print(f"Status: {response['ResponseMetadata']['HTTPStatusCode']}")