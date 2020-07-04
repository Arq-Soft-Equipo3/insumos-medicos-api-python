from enum import Enum


class ApplicationStatus(Enum):
    PENDING = 'Pending'
    ACCEPTED = 'Accepted'
    CANCELED = 'Canceled'
    REJECTED = 'Rejected'
