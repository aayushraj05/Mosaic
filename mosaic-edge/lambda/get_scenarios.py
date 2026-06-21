import json
from datetime import datetime, timedelta
import random


def lambda_handler(event, context):
    print("Received:", json.dumps(event))

    try:
        params   = event.get(
                  'queryStringParameters') or {}
        scenario = params.get('type', 'ideal')

        data = generate_scenario(scenario)

        return respond(200, data)

    except Exception as e:
        print(f"Lambda 7 error: {e}")
        return respond(500, {'error': str(e)})


def generate_scenario(scenario_type):
    base_time = datetime.utcnow()

    ZONE_CONFIG = {
        'mosaic-node-01': {
            'zone_id': 'A', 'zone_name': 'Zone Alpha — NW',
            'zone_color': '#00ff88',
            'lat': 19.0800, 'lon': 72.8760
        },
        'mosaic-node-02': {
            'zone_id': 'B', 'zone_name': 'Zone Beta — NE',
            'zone_color': '#00aaff',
            'lat': 19.0800, 'lon': 72.8800
        },
        'mosaic-node-03': {
            'zone_id': 'C', 'zone_name': 'Zone Gamma — SW',
            'zone_color': '#ffaa00',
            'lat': 19.0750, 'lon': 72.8760
        },
        'mosaic-node-04': {
            'zone_id': 'D', 'zone_name': 'Zone Delta — SE',
            'zone_color': '#ff44aa',
            'lat': 19.0750, 'lon': 72.8800
        }
    }

    def make_drone(node_id, battery,
                   status, detections,
                   victims, extra={}):
        zone = ZONE_CONFIG[node_id]
        base = {
            'device_id':         node_id,
            'zone_id':           zone['zone_id'],
            'zone_name':         zone['zone_name'],
            'zone_color':        zone['zone_color'],
            'lat':               str(zone['lat']),
            'lon':               str(zone['lon']),
            'display_status':    status,
            'battery_pct':       str(battery),
            'battery_health':    (
                'GOOD' if battery > 50 else
                'LOW'  if battery > 20 else
                'CRITICAL'),
            'last_seen':         base_time.isoformat(),
            'detections_today':  str(detections),
            'confirmed_victims': str(victims),
            'temperature_c':     str(round(
                50 + random.uniform(-5, 10), 1)),
            'cpu_usage_pct':     str(round(
                60 + random.uniform(-10, 20), 1)),
            'signal_dbm':        str(random.randint(
                -75, -45)),
            'altitude_m':        str(round(
                45 + random.uniform(-5, 15), 1)),
            'speed_ms':          str(round(
                4 + random.uniform(-1, 2), 1))
        }
        base.update(extra)
        return base

    # ─────────────────────
    # SCENARIO 1 — IDEAL
    # ─────────────────────
    if scenario_type == 'ideal':
        return {
            'scenario':    'ideal',
            'description': 'All systems operational. '
                           'All drones in assigned zones. '
                           'High confidence detections.',
            'drones': [
                make_drone('mosaic-node-01',
                           85, 'ACTIVE', 12, 10),
                make_drone('mosaic-node-02',
                           92, 'ACTIVE', 8, 7),
                make_drone('mosaic-node-03',
                           78, 'ACTIVE', 15, 13),
                make_drone('mosaic-node-04',
                           88, 'ACTIVE', 10, 9)
            ],
            'detections': [
                {
                    'device_id':    'mosaic-node-01',
                    'zone_id':      'A',
                    'zone_name':    'Zone Alpha — NW',
                    'timestamp':    base_time.isoformat(),
                    'status':       'confirmed',
                    'confidence':   '0.91',
                    'priority':     'CRITICAL',
                    'expression':   'fear',
                    'pose_indicators': json.dumps([
                        'fallen',
                        'possibly_unconscious'])
                },
                {
                    'device_id':    'mosaic-node-02',
                    'zone_id':      'B',
                    'zone_name':    'Zone Beta — NE',
                    'timestamp':    (base_time -
                        timedelta(minutes=2)).isoformat(),
                    'status':       'confirmed',
                    'confidence':   '0.87',
                    'priority':     'HIGH',
                    'expression':   'fear',
                    'pose_indicators': json.dumps([
                        'both_arms_raised', 'waving'])
                },
                {
                    'device_id':    'mosaic-node-03',
                    'zone_id':      'C',
                    'zone_name':    'Zone Gamma — SW',
                    'timestamp':    (base_time -
                        timedelta(minutes=5)).isoformat(),
                    'status':       'confirmed',
                    'confidence':   '0.83',
                    'priority':     'HIGH',
                    'expression':   'sad',
                    'pose_indicators': json.dumps([
                        'arms_raised', 'upright'])
                }
            ],
            'system_health': {
                'overall':              'OPERATIONAL',
                'active_drones':        4,
                'offline_drones':       0,
                'critical_drones':      0,
                'victims_confirmed':    39,
                'pending_review':       0,
                'avg_confidence':       0.87,
                'false_positive_rate':  0.05,
                'all_zones_covered':    True
            }
        }

    # ─────────────────────────
    # SCENARIO 2 — LOW BATTERY
    # ─────────────────────────
    elif scenario_type == 'low_battery':
        return {
            'scenario':    'low_battery',
            'description': 'Two drones critical battery. '
                           'Zones B and C partially uncovered.',
            'drones': [
                make_drone('mosaic-node-01',
                           82, 'ACTIVE', 12, 10),
                make_drone('mosaic-node-02',
                           8,  'CRITICAL', 3, 2,
                           {'display_status': 'CRITICAL',
                            'flight_mode': 'RTH_WARNING'}),
                make_drone('mosaic-node-03',
                           18, 'LOW_BATTERY', 7, 5,
                           {'display_status':
                            'LOW_BATTERY'}),
                make_drone('mosaic-node-04',
                           71, 'ACTIVE', 9, 8)
            ],
            'alerts': [
                {
                    'type':      'BATTERY_CRITICAL',
                    'device_id': 'mosaic-node-02',
                    'zone_id':   'B',
                    'zone_name': 'Zone Beta — NE',
                    'message':   'Battery 8% — '
                                 'Zone B uncovered soon',
                    'severity':  'CRITICAL'
                },
                {
                    'type':      'BATTERY_LOW',
                    'device_id': 'mosaic-node-03',
                    'zone_id':   'C',
                    'zone_name': 'Zone Gamma — SW',
                    'message':   'Battery 18% — '
                                 'Return recommended',
                    'severity':  'WARNING'
                }
            ],
            'system_health': {
                'overall':          'DEGRADED',
                'active_drones':    2,
                'critical_drones':  2,
                'zones_covered':    2,
                'zones_at_risk':    2,
                'victims_confirmed':25
            }
        }

    # ─────────────────────────
    # SCENARIO 3 — DRONE OFFLINE
    # ─────────────────────────
    elif scenario_type == 'drone_offline':
        return {
            'scenario':    'drone_offline',
            'description': 'Node 02 and 04 offline. '
                           'Zones B and D unmonitored.',
            'drones': [
                make_drone('mosaic-node-01',
                           75, 'ACTIVE', 12, 10),
                make_drone('mosaic-node-02',
                           0, 'OFFLINE', 3, 2,
                           {
                            'is_offline': True,
                            'last_seen': (base_time -
                                timedelta(minutes=8)
                                ).isoformat()
                           }),
                make_drone('mosaic-node-03',
                           68, 'ACTIVE', 7, 6),
                make_drone('mosaic-node-04',
                           0, 'OFFLINE', 9, 7,
                           {
                            'is_offline': True,
                            'last_seen': (base_time -
                                timedelta(minutes=14)
                                ).isoformat()
                           })
            ],
            'alerts': [
                {
                    'type':      'DRONE_OFFLINE',
                    'device_id': 'mosaic-node-02',
                    'zone_id':   'B',
                    'zone_name': 'Zone Beta — NE',
                    'message':   'No signal 8 min — '
                                 'Zone B UNMONITORED',
                    'severity':  'CRITICAL'
                },
                {
                    'type':      'DRONE_OFFLINE',
                    'device_id': 'mosaic-node-04',
                    'zone_id':   'D',
                    'zone_name': 'Zone Delta — SE',
                    'message':   'No signal 14 min — '
                                 'Zone D UNMONITORED',
                    'severity':  'CRITICAL'
                }
            ],
            'system_health': {
                'overall':          'CRITICAL',
                'active_drones':    2,
                'offline_drones':   2,
                'zones_covered':    2,
                'zones_unmonitored':2
            }
        }

    # ─────────────────────────
    # SCENARIO 4 — CORRUPTED DATA
    # ─────────────────────────
    elif scenario_type == 'corrupted_data':
        return {
            'scenario':    'corrupted_data',
            'description': 'Sensor corruption on nodes '
                           '02 and 03. Data flagged invalid.',
            'drones': [
                make_drone('mosaic-node-01',
                           80, 'ACTIVE', 12, 10),
                make_drone('mosaic-node-02',
                           65, 'ACTIVE', 0, 0,
                           {'detection_status': 'ERROR',
                            'sensor_error':
                            'Camera feed corrupted'}),
                make_drone('mosaic-node-03',
                           70, 'ACTIVE', 0, 0,
                           {'detection_status': 'ERROR',
                            'sensor_error':
                            'Confidence out of range'}),
                make_drone('mosaic-node-04',
                           85, 'ACTIVE', 9, 8)
            ],
            'corrupted_detections': [
                {
                    'device_id':  'mosaic-node-02',
                    'zone_id':    'B',
                    'timestamp':  base_time.isoformat(),
                    'status':     'error',
                    'confidence': '-1',
                    'error':      'Invalid confidence — '
                                  'sensor malfunction',
                    'raw_data':   'CORRUPTED'
                },
                {
                    'device_id':  'mosaic-node-03',
                    'zone_id':    'C',
                    'timestamp':  base_time.isoformat(),
                    'status':     'error',
                    'confidence': '999',
                    'error':      'Confidence out of '
                                  'range 0-1',
                    'raw_data':   'OUT_OF_BOUNDS'
                }
            ],
            'alerts': [
                {
                    'type':     'DATA_CORRUPTED',
                    'zone_id':  'B',
                    'message':  'Zone B — invalid sensor '
                                'data. Manual check needed.',
                    'severity': 'WARNING'
                },
                {
                    'type':     'DATA_CORRUPTED',
                    'zone_id':  'C',
                    'message':  'Zone C — confidence '
                                'out of bounds.',
                    'severity': 'WARNING'
                }
            ],
            'system_health': {
                'overall':       'WARNING',
                'data_quality':  'DEGRADED',
                'valid_nodes':   2,
                'error_nodes':   2,
                'zones_healthy': 2,
                'zones_error':   2
            }
        }

    # ─────────────────────────────────
    # SCENARIO 5 — HIGH FALSE POSITIVE
    # ─────────────────────────────────
    elif scenario_type == 'high_false_positive':
        return {
            'scenario':    'high_false_positive',
            'description': 'Zone A showing high false '
                           'positives. Threshold adapting.',
            'drones': [
                make_drone('mosaic-node-01',
                           78, 'ACTIVE', 18, 4,
                           {'false_positives': '14',
                            'zone_fp_rate': '0.78'}),
                make_drone('mosaic-node-02',
                           85, 'ACTIVE', 8, 7),
                make_drone('mosaic-node-03',
                           90, 'ACTIVE', 10, 9),
                make_drone('mosaic-node-04',
                           82, 'ACTIVE', 6, 5)
            ],
            'adaptation_log': [
                {
                    'timestamp': (base_time -
                        timedelta(minutes=15)
                        ).isoformat(),
                    'threshold': '0.60',
                    'event':     'Initial threshold',
                    'fp_rate':   '0.10'
                },
                {
                    'timestamp': (base_time -
                        timedelta(minutes=10)
                        ).isoformat(),
                    'threshold': '0.65',
                    'event':     'Raised — FP rate 0.42',
                    'fp_rate':   '0.42'
                },
                {
                    'timestamp': (base_time -
                        timedelta(minutes=5)
                        ).isoformat(),
                    'threshold': '0.70',
                    'event':     'Raised — FP rate 0.67',
                    'fp_rate':   '0.67'
                },
                {
                    'timestamp': base_time.isoformat(),
                    'threshold': '0.75',
                    'event':     'Stabilizing',
                    'fp_rate':   '0.45'
                }
            ],
            'system_health': {
                'overall':              'WARNING',
                'false_positive_rate':  '78% in Zone A',
                'threshold_adapted':    True,
                'current_threshold':    0.75,
                'zones_affected':       ['A']
            }
        }

    # ─────────────────────────────────
    # SCENARIO 6 — MULTIPLE VICTIMS
    # ─────────────────────────────────
    elif scenario_type == 'multiple_victims':
        return {
            'scenario':    'multiple_victims',
            'description': 'Mass casualty event. '
                           'Multiple zones reporting victims.',
            'drones': [
                make_drone('mosaic-node-01',
                           70, 'ACTIVE', 8, 8),
                make_drone('mosaic-node-02',
                           65, 'ACTIVE', 6, 5),
                make_drone('mosaic-node-03',
                           80, 'ACTIVE', 5, 5),
                make_drone('mosaic-node-04',
                           75, 'ACTIVE', 4, 3)
            ],
            'detections': [
                {
                    'device_id':       'mosaic-node-01',
                    'zone_id':         'A',
                    'zone_name':       'Zone Alpha — NW',
                    'status':          'confirmed',
                    'confidence':      '0.94',
                    'priority':        'CRITICAL',
                    'expression':      'fear',
                    'pose_indicators': json.dumps([
                        'fallen',
                        'possibly_unconscious'])
                },
                {
                    'device_id':       'mosaic-node-01',
                    'zone_id':         'A',
                    'zone_name':       'Zone Alpha — NW',
                    'status':          'confirmed',
                    'confidence':      '0.89',
                    'priority':        'CRITICAL',
                    'expression':      'fear',
                    'pose_indicators': json.dumps([
                        'both_arms_raised',
                        'active_distress'])
                },
                {
                    'device_id':       'mosaic-node-02',
                    'zone_id':         'B',
                    'zone_name':       'Zone Beta — NE',
                    'status':          'confirmed',
                    'confidence':      '0.91',
                    'priority':        'HIGH',
                    'expression':      'sad',
                    'pose_indicators': json.dumps([
                        'arms_raised'])
                },
                {
                    'device_id':       'mosaic-node-03',
                    'zone_id':         'C',
                    'zone_name':       'Zone Gamma — SW',
                    'status':          'uncertain',
                    'confidence':      '0.55',
                    'priority':        'MEDIUM',
                    'expression':      'neutral',
                    'pose_indicators': json.dumps([
                        'upright'])
                }
            ],
            'system_health': {
                'overall':           'MASS_CASUALTY',
                'victims_confirmed': 21,
                'pending_review':    1,
                'zones_with_victims':['A', 'B', 'C'],
                'alert':             'MASS CASUALTY — '
                                     'All zones active'
            }
        }

    # Default
    return {
        'error': 'Unknown scenario type',
        'available': [
            'ideal',
            'low_battery',
            'drone_offline',
            'corrupted_data',
            'high_false_positive',
            'multiple_victims'
        ]
    }


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