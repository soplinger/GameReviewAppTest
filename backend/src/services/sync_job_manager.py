"""Background job manager for library sync operations."""

import asyncio
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, Optional, Any
from dataclasses import dataclass, field

from ..core.logging import get_logger

logger = get_logger(__name__)


class JobStatus(str, Enum):
    """Job execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class SyncJob:
    """Represents a library sync job."""
    
    job_id: str
    user_id: int
    platform: Optional[str]
    status: JobStatus = JobStatus.PENDING
    progress: int = 0  # 0-100
    total_games: int = 0
    synced_games: int = 0
    failed_games: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    result: Optional[Dict[str, Any]] = None


class SyncJobManager:
    """
    Manages background sync jobs.
    
    Provides simple in-memory job tracking and async execution.
    For production, consider using Celery/RQ with Redis.
    """
    
    def __init__(self):
        self._jobs: Dict[str, SyncJob] = {}
        self._tasks: Dict[str, asyncio.Task] = {}
        self._max_jobs = 1000  # Limit memory usage
    
    def create_job(self, user_id: int, platform: Optional[str] = None) -> str:
        """
        Create a new sync job.
        
        Args:
            user_id: User ID
            platform: Optional platform to sync
            
        Returns:
            Job ID
        """
        job_id = str(uuid.uuid4())
        job = SyncJob(
            job_id=job_id,
            user_id=user_id,
            platform=platform
        )
        
        self._jobs[job_id] = job
        self._cleanup_old_jobs()
        
        logger.info(
            "sync_job_created",
            job_id=job_id,
            user_id=user_id,
            platform=platform
        )
        
        return job_id
    
    def get_job(self, job_id: str) -> Optional[SyncJob]:
        """Get job by ID."""
        return self._jobs.get(job_id)
    
    def get_user_jobs(self, user_id: int, limit: int = 10) -> list[SyncJob]:
        """Get recent jobs for a user."""
        user_jobs = [
            job for job in self._jobs.values()
            if job.user_id == user_id
        ]
        # Sort by created_at descending
        user_jobs.sort(key=lambda j: j.created_at, reverse=True)
        return user_jobs[:limit]
    
    def start_job(self, job_id: str, coro):
        """
        Start executing a job in the background.
        
        Args:
            job_id: Job ID
            coro: Coroutine to execute
        """
        job = self._jobs.get(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        if job.status != JobStatus.PENDING:
            raise ValueError(f"Job {job_id} is not pending")
        
        job.status = JobStatus.RUNNING
        job.started_at = datetime.utcnow()
        
        # Create and store task
        task = asyncio.create_task(self._execute_job(job_id, coro))
        self._tasks[job_id] = task
        
        logger.info("sync_job_started", job_id=job_id)
    
    async def _execute_job(self, job_id: str, coro):
        """Execute job coroutine and update status."""
        job = self._jobs.get(job_id)
        if not job:
            return
        
        try:
            result = await coro
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            job.progress = 100
            job.result = result
            
            logger.info(
                "sync_job_completed",
                job_id=job_id,
                synced_games=job.synced_games,
                failed_games=job.failed_games
            )
            
        except asyncio.CancelledError:
            job.status = JobStatus.CANCELLED
            job.completed_at = datetime.utcnow()
            logger.warning("sync_job_cancelled", job_id=job_id)
            
        except Exception as e:
            job.status = JobStatus.FAILED
            job.completed_at = datetime.utcnow()
            job.error = str(e)
            
            logger.error(
                "sync_job_failed",
                job_id=job_id,
                error=str(e),
                exc_info=True
            )
            
        finally:
            # Cleanup task reference
            self._tasks.pop(job_id, None)
    
    def update_progress(
        self,
        job_id: str,
        progress: Optional[int] = None,
        total_games: Optional[int] = None,
        synced_games: Optional[int] = None,
        failed_games: Optional[int] = None
    ):
        """Update job progress."""
        job = self._jobs.get(job_id)
        if not job:
            return
        
        if progress is not None:
            job.progress = min(100, max(0, progress))
        if total_games is not None:
            job.total_games = total_games
        if synced_games is not None:
            job.synced_games = synced_games
        if failed_games is not None:
            job.failed_games = failed_games
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a running job."""
        job = self._jobs.get(job_id)
        if not job or job.status != JobStatus.RUNNING:
            return False
        
        task = self._tasks.get(job_id)
        if task and not task.done():
            task.cancel()
            logger.info("sync_job_cancel_requested", job_id=job_id)
            return True
        
        return False
    
    def _cleanup_old_jobs(self):
        """Remove old completed jobs to prevent memory bloat."""
        if len(self._jobs) <= self._max_jobs:
            return
        
        # Keep jobs sorted by creation time
        jobs_by_time = sorted(
            self._jobs.items(),
            key=lambda x: x[1].created_at
        )
        
        # Remove oldest completed/failed jobs
        removed = 0
        target = self._max_jobs // 2  # Remove half when limit reached
        
        for job_id, job in jobs_by_time:
            if removed >= target:
                break
            
            if job.status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED):
                self._jobs.pop(job_id, None)
                removed += 1
        
        if removed > 0:
            logger.info("cleaned_up_old_jobs", count=removed)


# Global job manager instance
sync_job_manager = SyncJobManager()
