import json
import boto3
from datetime import datetime

dynamodb = boto3.resource('dynamodb',
           region_name='ap-south-1')

ZONE_CONFIG = {
    'mosaic-node-01': {'zone_id': 'A',
                       'zone_name': 'Zone Alpha — NW'},
    'mosaic-node-02': {'zone_id': 'B',
                       'zone_name': 'Zone Beta — NE'},
    'mosaic-node-03': {'zone_id': 'C',
                       'zone_name': 'Zone Gamma — SW'},
    'mosaic-node-04': {'zone_id': 'D',
                       'zone_name': 'Zone Delta — SE'}
}


def lambda_handler(event, context):
    print("Received:", json.dumps(event))

    try:
        # Parse body
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        elif isinstance(event.get('body'), dict):
            body = event['body']
        else:
            body = event

        device_id = body.get('device_id',
                    body.get('drone_id', 'unknown'))
        timestamp = body.get('timestamp',
                    datetime.utcnow().isoformat())

        # Full telemetry fields
        power    = body.get('power', {})
        flight   = body.get('flight', {})
        location = body.get('location', {})
        sensors  = body.get('sensors', {})
        comms    = body.get('comms', {})
        mission  = body.get('mission_stats', {})
        env      = body.get('environment', {})

        battery  = float(power.get('battery_pct',
                   body.get('battery', 0)))

        if battery > 50:
            health = 'GOOD'
        elif battery > 20:
            health = 'LOW'
        elif battery > 5:
            health = 'CRITICAL'
        else:
            health = 'EMPTY'

        zone = ZONE_CONFIG.get(device_id, {
            'zone_id':   'X',
            'zone_name': 'Unassigned'
        })

        # Save to swarm_nodes
        table = dynamodb.Table('swarm_nodes')
        item  = {
            'device_id':         device_id,
            'last_seen':         timestamp,
            'status':            flight.get(
                                 'mode', 'ACTIVE'),
            'detection_status':  'scanning',
            'battery_pct':       str(battery),
            'battery_health':    health,
            'altitude_m':        str(flight.get(
                                 'altitude_m',
                                 body.get(
                                 'altitude', 0))),
            'speed_ms':          str(flight.get(
                                 'speed_ms', 0)),
            'heading_deg':       str(flight.get(
                                 'heading_deg', 0)),
            'lat':               str(location.get(
                                 'lat',
                                 body.get(
                                 'gps_lat', 0))),
            'lon':               str(location.get(
                                 'lon',
                                 body.get(
                                 'gps_lon', 0))),
            'temperature_c':     str(sensors.get(
                                 'temperature_c', 0)),
            'cpu_usage_pct':     str(sensors.get(
                                 'cpu_usage_pct', 0)),
            'ram_used_mb':       str(sensors.get(
                                 'ram_used_mb', 0)),
            'signal_dbm':        str(comms.get(
                                 'signal_dbm', 0)),
            'packet_loss_pct':   str(comms.get(
                                 'packet_loss_pct', 0)),
            'detections_today':  str(mission.get(
                                 'detections_today', 0)),
            'confirmed_victims': str(mission.get(
                                 'confirmed_victims', 0)),
            'wind_speed_ms':     str(env.get(
                                 'wind_speed_ms', 0)),
            'rain_detected':     str(env.get(
                                 'rain_detected',
                                 False)),
            'zone_id':           zone['zone_id'],
            'zone_name':         zone['zone_name'],
            'simulated':         str(body.get(
                                 'simulated', False)),
            'updated_at':        datetime.utcnow(
                                 ).isoformat()
        }

        table.put_item(Item=item)
        print(f"Heartbeat from {device_id} "
              f"zone={zone['zone_id']} "
              f"batt={battery}%")

        return respond(200, {
            'message':     'Heartbeat recorded',
            'device_id':   device_id,
            'zone_id':     zone['zone_id'],
            'zone_name':   zone['zone_name'],
            'battery_pct': battery,
            'health':      health
        })

    except Exception as e:
        print(f"Lambda 6 error: {e}")
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