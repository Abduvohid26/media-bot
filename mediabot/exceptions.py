class InstanceQuotaLimitReachedException(Exception):
  pass

class InstanceRequestRateLimitReached(Exception):
  def __init__(self):
    pass

class AccessDeniedException(Exception):
  pass
