UPDATE
  "broadcast"
SET
  "cursor" = %(cursor)s,
  "succeeded_jobs" = "succeeded_jobs" + COALESCE(%(succeeded_jobs)s, 0),
  "failed_jobs" = "failed_jobs" + COALESCE(%(failed_jobs)s, 0),
  "blocked_jobs" = "blocked_jobs" + COALESCE(%(blocked_jobs)s, 0)
WHERE
  "id" = %(broadcast_id)s;