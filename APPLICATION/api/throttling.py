from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class BurstRateUserThrottle(UserRateThrottle):
    scope = 'burst_user'


class SustainedRateUserThrottle(UserRateThrottle):
    scope = 'sustained_user'


class BurstRateAnonThrottle(AnonRateThrottle):
    scope = 'burst_anon'


class SustainedRateAnonThrottle(AnonRateThrottle):
    scope = 'sustained_anon'
