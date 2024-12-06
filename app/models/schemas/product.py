
from enum import Enum
from pydantic import BaseModel, Field



        
class Product(BaseModel):
    class ProductType(tuple, Enum):   
        monthly = (1, "BellyBook月度会员")
        annual = (2, "BellyBook年度会员")
        gourmet = (3, "BellyBook美食家年度会员")
        permanent = (99, "BellyBook永久会员")

    id: int
    name: str
    type: ProductType 