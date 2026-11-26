from datetime import datetime

from backend.common.model.contract_model import ContractModel


class UserDTO(ContractModel):
    id: int
    username: str
    password_hash: str
    mail: str
    status: int
    created_by: int
    updated_by: int
    created_at: datetime
    updated_at: datetime
    delete_flg: int
