from src import applicationStatus
from src.applicationStatus import ApplicationStatus


class Application:
    def __init__(self, anEmailAddress, supplyName, area):
        self.assertFieldsNotEmpty(anEmailAddress, supplyName, area)
        self.applicationID = None
        self.filler = anEmailAddress
        self.supply = supplyName
        self.area = area
        self.status = ApplicationStatus.PENDING.value

    @classmethod
    def assertFieldsNotEmpty(cls, anEmailAddress, supplyName, area):
        if anEmailAddress is None or supplyName is None or area is None:
            raise ValueError('Instance creation Failed')

    def cancelApplication(self):
        self.status = ApplicationStatus.CANCELED.value

    def approveApplication(self):
        if self.status != ApplicationStatus.CANCELED.value:
            self.status = ApplicationStatus.ACCEPTED.value
        else:
            raise ValueError('Canceled applications cannot be approved')
