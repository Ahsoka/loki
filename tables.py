from sqlalchemy import Column, SmallInteger, Enum, String, Float, ForeignKey
from enums import Contributors, Manufacturer, StorageType, FormFactor, Usage
from sqlalchemy.orm.decl_api import registry
from dataclasses import dataclass, field
from typing import Union

mapper = registry()


@mapper.mapped
@dataclass
class Storage:
    __tablename__ = 'storage'

    __sa_dataclass_metadata_key__ = 'sa'

    id: int = field(
        init=False,
        metadata={'sa': Column(SmallInteger, primary_key=True)}
    )
    manufacturer: Manufacturer = field(metadata={
        'sa': Column(Enum(Manufacturer), nullable=False)
    })
    model_number: str = field(metadata={'sa': Column(String, nullable=False)})
    capacity_tb: float = field(metadata={'sa': Column(Float, nullable=False)})
    ampere: float = field(metadata={'sa': Column(Float, nullable=False)})
    storage_type: StorageType = field(
        metadata={'sa': Column(Enum(StorageType), nullable=False)}
    )
    form_factor: FormFactor = field(
        metadata={'sa': Column(Enum(FormFactor), nullable=False)}
    )
    rpm: int = field(metadata={'sa': Column(SmallInteger)}, default=None)
    usage: Usage = field(
        metadata={'sa': Column(Enum(Usage), nullable=False)},
        default=Usage.permanent
    )
    voltage: int = field(
        metadata={'sa': Column(SmallInteger, nullable=False)},
        default=5
    )
    link: Union[str, None] = field(default=None, metadata={'sa': Column(String)})
    notes: Union[str, None] = field(
        default=None, metadata={'sa': Column(String)}
    )
    purchase_id: int = field(
        default=None,
        metadata={'sa': Column(SmallInteger, ForeignKey('purchases.id'))}
    )


@mapper.mapped
@dataclass
class Purchase:
    __tablename__ = 'purchases'

    id: int = field(
        init=False,
        metadata={'sa': Column(SmallInteger, primary_key=True)}
    )
    name: str = field(metadata={'sa': Column(String, nullable=False)})
    base_price: float = field(metadata={'sa': Column(Float, nullable=False)})
    shipping: float = field(metadata={'sa': Column(Float)}, default=0.0)
    tax: float = field(metadata={'sa': Column(Float)}, default=0.0)
    notes: str = field(metadata={'sa': Column(String)}, default=None)


@mapper.mapped
@dataclass
class Buyer:
    __tablename__ = 'buyer'

    name: Contributors = field(metadata={'sa': Column(Enum(Contributors), primary_key=True)})
    purchase_id: int = field(metadata={
        'sa': Column(SmallInteger, ForeignKey(Purchase.id), primary_key=True)
    })
