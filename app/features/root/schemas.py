from pydantic import BaseModel


class ServiceInfo(BaseModel):
    service: str
    environment: str
    version: str
