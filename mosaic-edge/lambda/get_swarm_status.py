import json
import boto3
from datetime import datetime

dynamodb = boto3.resource('dynamodb',
           region_name='ap-south-1')

# Zone assignments
ZONE_CONFIG = {
    'mosaic-node-01': {
        'zone_id':    'A',
        'zone_name':  'Zone Alpha — NW',
        'zone_color': '#00ff88',
        'lat_min':    19.078,
        'lat_max':    19.082,
        'lon_min':    72.875,
        'lon_max':    72.878,
        'drone_type': 'real'
    },
    'mosaic-node-02': {
        'zone_id':    'B',
        'zone_name':  'Zone Beta — NE',
        'zone_color': '#00aaff',
        'lat_min':    19.078,
        'lat_max':    19.082,
        'lon_min':    72.878,
        'lon_max':    72.882,
        'drone_type': 'simulated'
    },
    'mosaic-node-03': {
        'zone_id':    'C',
        'zone_name':  'Zone Gamma — SW',
        'zone_color': '#ffaa00',
        'lat_min':    19.074,
        'lat_max':    19.078,
        'lon_min':    72.875,
        'lon_max':    72.878,
        'drone_type': 'simulated'
    },
    'mosaic-node-04': {
        'zone_id':    'D',
        'zone_name':  'Zone Delta — SE',
        'zone_color': '#ff44aa',
        'lat_min':    19.074,
        'lat_max':    19.078,
        'lon_min':    72.878,
        'lon_max':    72.882,
        'drone_type': 'simulated'
    }
}


def lambda_handler(event, context):
    print("Received:", json.dumps(event))

    try:
        table    = dynamodb.Table('swarm_nodes')
        response = table.scan()
        items    = response.get('Items', [])

        now   = datetime.utcnow()
        nodes = []

        for item in items:
            device_id     = item.get('device_id', '')
            last_seen_str = item.get('last_seen', '')
            is_offline    = False

            try:
                last_seen  = datetime.fromisoformat(
                    last_seen_str)
                diff       = (now - last_seen
                              ).total_seconds()
                is_offline = diff > 120
            except Exception:
                is_offline = True

            battery     = float(
                item.get('battery_pct', 0))
            flight_mode = item.get('status', 'UNKNOWN')

            if is_offline:
                display_status = 'OFFLINE'
            elif battery <= 5:
                display_status = 'EMPTY'
            elif battery <= 20:
                display_status = 'CRITICAL'
            elif battery <= 50:
                display_status = 'LOW_BATTERY'
            elif flight_mode in ['RTH',
                                  'RTH_WARNING']:
                display_status = flight_mode
            else:
                display_status = 'ACTIVE'

            # Get zone info
            zone = ZONE_CONFIG.get(device_id, {
                'zone_id':    'X',
                'zone_name':  'Unassigned',
                'zone_color': '#888888',
                'lat_min':    0,
                'lat_max':    0,
                'lon_min':    0,
                'lon_max':    0,
                'drone_type': 'unknown'
            })

            # Check if drone is in its zone
            try:
                lat = float(item.get('lat', 0))
                lon = float(item.get('lon', 0))
                in_zone = (
                    zone['lat_min'] <= lat <=
                    zone['lat_max'] and
                    zone['lon_min'] <= lon <=
                    zone['lon_max']
                )
            except Exception:
                in_zone = False

            nodes.append({
                'device_id':         device_id,
                'last_seen':         last_seen_str,
                'is_offline':        is_offline,
                'display_status':    display_status,
                'flight_mode':       flight_mode,
                'detection_status':  item.get(
                    'detection_status', 'scanning'),

                # Zone
                'zone_id':           zone['zone_id'],
                'zone_name':         zone['zone_name'],
                'zone_color':        zone['zone_color'],
                'zone_bounds': {
                    'lat_min': zone['lat_min'],
                    'lat_max': zone['lat_max'],
                    'lon_min': zone['lon_min'],
                    'lon_max': zone['lon_max']
                },
                'in_assigned_zone':  in_zone,
                'drone_type':        zone['drone_type'],

                # Power
                'battery_pct':       item.get(
                    'battery_pct'),
                'battery_health':    item.get(
                    'battery_health'),

                # Flight
                'altitude_m':        item.get(
                    'altitude_m'),
                'speed_ms':          item.get(
                    'speed_ms'),
                'heading_deg':       item.get(
                    'heading_deg'),

                # Location
                'lat':               item.get('lat'),
                'lon':               item.get('lon'),
                'in_zone':           in_zone,

                # Sensors
                'temperature_c':     item.get(
                    'temperature_c'),
                'cpu_usage_pct':     item.get(
                    'cpu_usage_pct'),
                'signal_dbm':        item.get(
                    'signal_dbm'),

                # Mission
                'detections_today':  item.get(
                    'detections_today'),
                'confirmed_victims': item.get(
                    'confirmed_victims'),
                'simulated':         item.get(
                    'simulated')
            })

        # Sort by zone
        nodes.sort(key=lambda x: x.get(
            'zone_id', 'Z'))

        total    = len(nodes)
        active   = sum(1 for n in nodes if
                       n['display_status'] == 'ACTIVE')
        offline  = sum(1 for n in nodes if
                       n['is_offline'])
        critical = sum(1 for n in nodes if
                       n['display_status'] in
                       ['CRITICAL', 'EMPTY'])
        in_zone  = sum(1 for n in nodes if
                       n['in_assigned_zone'])

        return respond(200, {
            'total_nodes':       total,
            'active_nodes':      active,
            'offline_nodes':     offline,
            'critical_nodes':    critical,
            'in_zone_count':     in_zone,
            'zone_config':       ZONE_CONFIG,
            'nodes':             nodes,
            'server_time':       now.isoformat()
        })

    except Exception as e:
        print(f"Lambda 4 error: {e}")
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