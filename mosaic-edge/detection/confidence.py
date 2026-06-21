# detection/confidence.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import config


class ConfidenceAssembler:

    def compute(self, yolo_score, pose_score,
                expression, expression_score):

        urgent = ['fear', 'sad', 'angry', 'disgust']
        expr_urgency = (expression_score
                        if expression in urgent
                        else expression_score * 0.3)

        final_score = round(
            (yolo_score    * config.CONFIDENCE_WEIGHT) +
            (pose_score    * config.POSE_WEIGHT) +
            (expr_urgency  * config.EXPRESSION_WEIGHT),
            3
        )

        if final_score >= config.THRESHOLD:
            status = 'confirmed'
        elif final_score >= config.FLOOR:
            status = 'uncertain'
        elif yolo_score > 0:
            status = 'possible_missed_victim'
        else:
            status = 'no_detection'

        priority = self._get_priority(
            status, expression, final_score)

        return {
            'final_score': final_score,
            'status':      status,
            'priority':    priority
        }

    def _get_priority(self, status,
                      expression, score):
        if score >= 0.85:
            return 'CRITICAL'
        if status == 'confirmed':
            if expression in ['fear', 'sad', 'angry']:
                return 'HIGH'
            return 'MEDIUM'
        if status == 'uncertain':
            return 'MEDIUM'
        return 'LOW'
