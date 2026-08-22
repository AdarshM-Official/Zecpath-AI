# Scalability & Horizontal Scaling Strategy

## 1. Architecture Shift
To support enterprise loads (e.g., thousands of simultaneous candidate interviews), Zecpath-AI must transition from a monolithic Flask application into a scalable, stateless microservice architecture deployed on Kubernetes.

## 2. Statelessness & Caching
- **Session State:** The in-memory `SESSIONS` and `REPORTS` dictionaries in `api/hr_interview_api.py` must be migrated to **Redis**. This allows any instance of the API to serve any candidate request.
- **Config State:** Configurations (as optimized on Day 60) remain cached locally in memory via `lru_cache`, synced via a fast boot script.

## 3. Load Balancing Strategy
1. **Application Load Balancer (ALB):** Distributes incoming HTTP requests (Resume uploads, Interview Text messaging) via a **Round-Robin** algorithm across all active AI API Pods.
2. **Sticky Sessions for WebSockets:** Behavioral tracking (gaze estimation, head pose) streams over WebSockets. The load balancer must use IP-based sticky sessions to keep the WebSocket connection bound to a specific pod for the duration of the interview.

## 4. Autoscaling (HPA)
Deploy a **Horizontal Pod Autoscaler (HPA)** in Kubernetes configured with dual-metrics:
- **CPU Utilization:** Scale out when average CPU > 70% (indicates heavy NLP inference load).
- **Queue Depth:** The `AsyncBatchProcessor` pulls from a Celery/RabbitMQ queue. If the `resume_parsing` queue depth exceeds 500 items, Kubernetes automatically spins up dedicated asynchronous worker pods.

## 5. Database Sharding
- **Transcripts:** Move raw interview transcripts (which grow rapidly) to a NoSQL document store (MongoDB) sharded by `tenant_id` (Company).
- **Relational Data:** Keep final scores, metadata, and roles in PostgreSQL, implementing read-replicas for recruiter dashboard queries to prevent heavy read-loads from impacting active interview writes.
