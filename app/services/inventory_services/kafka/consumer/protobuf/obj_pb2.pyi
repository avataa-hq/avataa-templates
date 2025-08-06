from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MO(_message.Message):
    __slots__ = ("id", "name", "pov", "geometry", "active", "latitude", "longitude", "tmo_id", "p_id", "point_a_id", "point_b_id", "model", "version", "status", "creation_date", "modification_date", "document_count", "label")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    POV_FIELD_NUMBER: _ClassVar[int]
    GEOMETRY_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_FIELD_NUMBER: _ClassVar[int]
    LATITUDE_FIELD_NUMBER: _ClassVar[int]
    LONGITUDE_FIELD_NUMBER: _ClassVar[int]
    TMO_ID_FIELD_NUMBER: _ClassVar[int]
    P_ID_FIELD_NUMBER: _ClassVar[int]
    POINT_A_ID_FIELD_NUMBER: _ClassVar[int]
    POINT_B_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CREATION_DATE_FIELD_NUMBER: _ClassVar[int]
    MODIFICATION_DATE_FIELD_NUMBER: _ClassVar[int]
    DOCUMENT_COUNT_FIELD_NUMBER: _ClassVar[int]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    id: int
    name: str
    pov: _struct_pb2.Struct
    geometry: _struct_pb2.Struct
    active: bool
    latitude: float
    longitude: float
    tmo_id: int
    p_id: int
    point_a_id: int
    point_b_id: int
    model: str
    version: int
    status: str
    creation_date: _timestamp_pb2.Timestamp
    modification_date: _timestamp_pb2.Timestamp
    document_count: int
    label: str
    def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ..., pov: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., geometry: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., active: bool = ..., latitude: _Optional[float] = ..., longitude: _Optional[float] = ..., tmo_id: _Optional[int] = ..., p_id: _Optional[int] = ..., point_a_id: _Optional[int] = ..., point_b_id: _Optional[int] = ..., model: _Optional[str] = ..., version: _Optional[int] = ..., status: _Optional[str] = ..., creation_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., modification_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., document_count: _Optional[int] = ..., label: _Optional[str] = ...) -> None: ...

class TMO(_message.Message):
    __slots__ = ("id", "name", "p_id", "icon", "description", "virtual", "global_uniqueness", "latitude", "longitude", "created_by", "modified_by", "creation_date", "modification_date", "primary", "version", "status", "lifecycle_process_definition", "materialize", "severity_id", "geometry_type", "points_constraint_by_tmo", "minimize", "label")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    P_ID_FIELD_NUMBER: _ClassVar[int]
    ICON_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    VIRTUAL_FIELD_NUMBER: _ClassVar[int]
    GLOBAL_UNIQUENESS_FIELD_NUMBER: _ClassVar[int]
    LATITUDE_FIELD_NUMBER: _ClassVar[int]
    LONGITUDE_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    MODIFIED_BY_FIELD_NUMBER: _ClassVar[int]
    CREATION_DATE_FIELD_NUMBER: _ClassVar[int]
    MODIFICATION_DATE_FIELD_NUMBER: _ClassVar[int]
    PRIMARY_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    LIFECYCLE_PROCESS_DEFINITION_FIELD_NUMBER: _ClassVar[int]
    MATERIALIZE_FIELD_NUMBER: _ClassVar[int]
    SEVERITY_ID_FIELD_NUMBER: _ClassVar[int]
    GEOMETRY_TYPE_FIELD_NUMBER: _ClassVar[int]
    POINTS_CONSTRAINT_BY_TMO_FIELD_NUMBER: _ClassVar[int]
    MINIMIZE_FIELD_NUMBER: _ClassVar[int]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    id: int
    name: str
    p_id: int
    icon: str
    description: str
    virtual: bool
    global_uniqueness: bool
    latitude: int
    longitude: int
    created_by: str
    modified_by: str
    creation_date: _timestamp_pb2.Timestamp
    modification_date: _timestamp_pb2.Timestamp
    primary: _containers.RepeatedScalarFieldContainer[int]
    version: int
    status: int
    lifecycle_process_definition: str
    materialize: bool
    severity_id: int
    geometry_type: str
    points_constraint_by_tmo: _containers.RepeatedScalarFieldContainer[int]
    minimize: bool
    label: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ..., p_id: _Optional[int] = ..., icon: _Optional[str] = ..., description: _Optional[str] = ..., virtual: bool = ..., global_uniqueness: bool = ..., latitude: _Optional[int] = ..., longitude: _Optional[int] = ..., created_by: _Optional[str] = ..., modified_by: _Optional[str] = ..., creation_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., modification_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., primary: _Optional[_Iterable[int]] = ..., version: _Optional[int] = ..., status: _Optional[int] = ..., lifecycle_process_definition: _Optional[str] = ..., materialize: bool = ..., severity_id: _Optional[int] = ..., geometry_type: _Optional[str] = ..., points_constraint_by_tmo: _Optional[_Iterable[int]] = ..., minimize: bool = ..., label: _Optional[_Iterable[int]] = ...) -> None: ...

class TPRM(_message.Message):
    __slots__ = ("id", "name", "description", "val_type", "multiple", "required", "returnable", "constraint", "prm_link_filter", "group", "tmo_id", "created_by", "modified_by", "creation_date", "modification_date", "version", "field_value")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    VAL_TYPE_FIELD_NUMBER: _ClassVar[int]
    MULTIPLE_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_FIELD_NUMBER: _ClassVar[int]
    RETURNABLE_FIELD_NUMBER: _ClassVar[int]
    CONSTRAINT_FIELD_NUMBER: _ClassVar[int]
    PRM_LINK_FILTER_FIELD_NUMBER: _ClassVar[int]
    GROUP_FIELD_NUMBER: _ClassVar[int]
    TMO_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    MODIFIED_BY_FIELD_NUMBER: _ClassVar[int]
    CREATION_DATE_FIELD_NUMBER: _ClassVar[int]
    MODIFICATION_DATE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    FIELD_VALUE_FIELD_NUMBER: _ClassVar[int]
    id: int
    name: str
    description: str
    val_type: str
    multiple: bool
    required: bool
    returnable: bool
    constraint: str
    prm_link_filter: str
    group: str
    tmo_id: int
    created_by: str
    modified_by: str
    creation_date: _timestamp_pb2.Timestamp
    modification_date: _timestamp_pb2.Timestamp
    version: int
    field_value: str
    def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., val_type: _Optional[str] = ..., multiple: bool = ..., required: bool = ..., returnable: bool = ..., constraint: _Optional[str] = ..., prm_link_filter: _Optional[str] = ..., group: _Optional[str] = ..., tmo_id: _Optional[int] = ..., created_by: _Optional[str] = ..., modified_by: _Optional[str] = ..., creation_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., modification_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., version: _Optional[int] = ..., field_value: _Optional[str] = ...) -> None: ...

class PRM(_message.Message):
    __slots__ = ("id", "value", "tprm_id", "mo_id", "version")
    ID_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    TPRM_ID_FIELD_NUMBER: _ClassVar[int]
    MO_ID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    id: int
    value: str
    tprm_id: int
    mo_id: int
    version: int
    def __init__(self, id: _Optional[int] = ..., value: _Optional[str] = ..., tprm_id: _Optional[int] = ..., mo_id: _Optional[int] = ..., version: _Optional[int] = ...) -> None: ...

class ListMO(_message.Message):
    __slots__ = ("objects",)
    OBJECTS_FIELD_NUMBER: _ClassVar[int]
    objects: _containers.RepeatedCompositeFieldContainer[MO]
    def __init__(self, objects: _Optional[_Iterable[_Union[MO, _Mapping]]] = ...) -> None: ...

class ListTMO(_message.Message):
    __slots__ = ("objects",)
    OBJECTS_FIELD_NUMBER: _ClassVar[int]
    objects: _containers.RepeatedCompositeFieldContainer[TMO]
    def __init__(self, objects: _Optional[_Iterable[_Union[TMO, _Mapping]]] = ...) -> None: ...

class ListTPRM(_message.Message):
    __slots__ = ("objects",)
    OBJECTS_FIELD_NUMBER: _ClassVar[int]
    objects: _containers.RepeatedCompositeFieldContainer[TPRM]
    def __init__(self, objects: _Optional[_Iterable[_Union[TPRM, _Mapping]]] = ...) -> None: ...

class ListPRM(_message.Message):
    __slots__ = ("objects",)
    OBJECTS_FIELD_NUMBER: _ClassVar[int]
    objects: _containers.RepeatedCompositeFieldContainer[PRM]
    def __init__(self, objects: _Optional[_Iterable[_Union[PRM, _Mapping]]] = ...) -> None: ...
