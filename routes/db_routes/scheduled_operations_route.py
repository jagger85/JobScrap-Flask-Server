from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from middlewares import user_or_admin_required
from helpers import get_user_from_jwt
from redbeat import RedBeatSchedulerEntry
from celery.schedules import crontab
from services import redbeat_scheduler
from services import celery
from uuid import uuid4
import json
from datetime import datetime

scheduled_scrap_operation_bp = Blueprint("scheduled_scrap_operation", __name__)

@scheduled_scrap_operation_bp.route("/api/scheduled_scrap_operations", methods=["GET"])
@user_or_admin_required
def get_all_scheduled_scrap_operations():
    tasks = []
    task_keys = [key for key in redbeat_scheduler.scan_iter('redbeat:*') 
                 if not ('::' in key or ':lock' in key)]
    
    for key in task_keys:
        try:
            entry = RedBeatSchedulerEntry.from_key(key, app=celery)
            tasks.append({
                'id': entry.name,
                'task': entry.task,
                'schedule': str(entry.schedule),
                'enabled': entry.enabled,
                'last_run_at': entry.last_run_at.isoformat() if entry.last_run_at else None,
                'total_run_count': entry.total_run_count,
                # Operation specific data
                'platform': entry.kwargs.get('platform'),
                'keywords': entry.kwargs.get('keywords'),
                'dateRange': entry.kwargs.get('dateRange'),
                'username': entry.kwargs.get('username')
            })
        except Exception as e:
            print(f"Error processing key {key}: {str(e)}")
            continue
    
    return jsonify(tasks), 200

@scheduled_scrap_operation_bp.route("/api/scheduled_scrap_operations", methods=["POST"])
@user_or_admin_required
def create_scheduled_scrap_operation():
    try:
        data = request.get_json(force=True)
        token = request.headers.get("Authorization")
        username = get_user_from_jwt(token)
        key_id = str(uuid4())
    
        # Create the scheduled task with operation data in kwargs
        interval = crontab(minute=f'*/{data["frequency"]}')
        entry = RedBeatSchedulerEntry(
            key_id,
            "tasks.celery_tasks.example_task",
            interval,
            kwargs={
                "platform": str(data.get('platform', '')),
                "username": str(username),
                "keywords": str(data.get('keywords', '')),
                "dateRange": str(data.get('dateRange', '')),
            },
            app=celery
        )
        entry.save()
        
        return jsonify({
            "message": "Scheduled scrap operation created successfully",
            "key_id": key_id
        }), 200
        
    except Exception as e:
        print(f"Error creating scheduled scrap operation: {str(e)}")
        return jsonify({"error": str(e)}), 500

@scheduled_scrap_operation_bp.route("/api/scheduled_scrap_operations/<id>", methods=["DELETE"])
@user_or_admin_required
def delete_scheduled_scrap_operation(id):
    try:
        # Delete the task from Redis
        entry = RedBeatSchedulerEntry.from_key(f'redbeat:{id}', app=celery)
        entry.delete()  # Remove the task from Redis
        return jsonify({"message": "Scheduled scrap operation deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@scheduled_scrap_operation_bp.route("/api/scheduled_scrap_operations/<id>/activate", methods=["PUT"])
@user_or_admin_required
def activate_scheduled_scrap_operation(id):
    # Activate the task in Redis
    try:
        entry = RedBeatSchedulerEntry.from_key(f'redbeat:{id}', app=celery)
        entry.enabled = True  # Set the task to enabled
        entry.save()  # Save the changes to Redis
        return jsonify({"message": "Scheduled scrap operation activated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@scheduled_scrap_operation_bp.route("/api/scheduled_scrap_operations/<id>/deactivate", methods=["PUT"])
@user_or_admin_required
def deactivate_scheduled_scrap_operation(id):
    # Deactivate the task in Redis
    try:
        entry = RedBeatSchedulerEntry.from_key(f'redbeat:{id}', app=celery)
        entry.enabled = False  # Set the task to disabled
        entry.save()  # Save the changes to Redis
        return jsonify({"message": "Scheduled scrap operation deactivated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


