from enum import Enum


class ApplicationStatus(Enum):
    PENDING = 'Pending'
    APPROVED = 'Approved'
    CANCELED = 'Canceled'
    REJECTED = 'Rejected'
