from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from application.common.uow import SQLAlchemyUoW, UoW
from application.paramater_validation.interactors import (
    ParameterValidationInteractor,
)
from application.template.read.interactors import TemplateReaderInteractor
from application.template_object.read.interactors import (
    TemplateObjectReaderInteractor,
)
from application.template_parameter.create.interactors import (
    TemplateParameterCreatorInteractor,
)
from application.template_parameter.read.interactors import (
    TemplateParameterReaderInteractor,
)
from application.template_parameter.update.interactors import (
    BulkTemplateParameterUpdaterInteractor,
    TemplateParameterUpdaterInteractor,
)
from database import get_session_factory
from domain.parameter_validation.query import TPRMReader
from domain.template.query import TemplateReader
from domain.template_object.query import TemplateObjectReader
from domain.template_parameter.command import (
    TemplateParameterCreator,
    TemplateParameterUpdater,
)
from domain.template_parameter.query import TemplateParameterReader
from infrastructure.db.template.read.gateway import SQLTemplateReaderRepository
from infrastructure.db.template_object.read.gateway import (
    SQLTemplateObjectReaderRepository,
)
from infrastructure.db.template_parameter.create.gateway import (
    SQLTemplateParameterCreatorRepository,
)
from infrastructure.db.template_parameter.read.gateway import (
    SQLTemplateParameterReaderRepository,
)
from infrastructure.db.template_parameter.update.gateway import (
    SQLTemplateParameterUpdaterRepository,
)
from infrastructure.grpc.tprm.read.gateway import GrpcTPRMReaderRepository


# Common
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_unit_of_work(session: AsyncSession = Depends(get_async_session)) -> UoW:
    return SQLAlchemyUoW(session)


# REPO
## Inventory Repo
def get_inventory_repository() -> TPRMReader:
    return GrpcTPRMReaderRepository()


## Template Repo
async def get_template_reader_repository(
    session: AsyncSession = Depends(get_async_session),
) -> TemplateReader:
    return SQLTemplateReaderRepository(session)


## Template object Repo
def get_template_object_reader_repository(
    session: AsyncSession = Depends(get_async_session),
) -> TemplateObjectReader:
    return SQLTemplateObjectReaderRepository(session)


## Template parameter Repo
def get_template_parameter_creator_repository(
    session: AsyncSession = Depends(get_async_session),
) -> TemplateParameterCreator:
    return SQLTemplateParameterCreatorRepository(session)


def get_template_parameter_reader_repository(
    session: AsyncSession = Depends(get_async_session),
) -> TemplateParameterReader:
    return SQLTemplateParameterReaderRepository(session)


def get_template_parameter_updater_repository(
    session: AsyncSession = Depends(get_async_session),
) -> TemplateParameterUpdater:
    return SQLTemplateParameterUpdaterRepository(session)


# INTERACTORS
## ParameterValidator Interactor
def get_template_parameter_validator_interactor(
    repository: TPRMReader = Depends(get_inventory_repository),
) -> ParameterValidationInteractor:
    return ParameterValidationInteractor(repository)


## Template Interactor
def read_template_interactor(
    repository: TemplateReader = Depends(get_template_reader_repository),
) -> TemplateReaderInteractor:
    return TemplateReaderInteractor(repository)


## Template Object Interactor
def read_template_object_interactor(
    to_repository: TemplateObjectReader = Depends(
        get_template_object_reader_repository
    ),
    tp_repository: TemplateParameterReader = Depends(
        get_template_parameter_reader_repository
    ),
) -> TemplateObjectReaderInteractor:
    return TemplateObjectReaderInteractor(
        to_repo=to_repository, tp_repo=tp_repository
    )


## Template Parameter Interactor
def create_template_parameter_interactor(
    uow: UoW = Depends(get_unit_of_work),
    to_repo: TemplateObjectReader = Depends(
        get_template_object_reader_repository
    ),
    tp_repo: TemplateParameterCreator = Depends(
        get_template_parameter_creator_repository
    ),
    tprm_validator: ParameterValidationInteractor = Depends(
        get_template_parameter_validator_interactor
    ),
) -> TemplateParameterCreatorInteractor:
    return TemplateParameterCreatorInteractor(
        to_repo=to_repo,
        tp_repo=tp_repo,
        tprm_validator=tprm_validator,
        uow=uow,
    )


def read_template_parameter_interactor(
    tp_repo: TemplateParameterReader = Depends(
        get_template_parameter_reader_repository
    ),
) -> TemplateParameterReaderInteractor:
    return TemplateParameterReaderInteractor(tp_repo)


def update_template_parameter_interactor(
    uow: UoW = Depends(get_unit_of_work),
    tp_reader: TemplateParameterReader = Depends(
        get_template_parameter_reader_repository
    ),
    to_reader: TemplateObjectReader = Depends(
        get_template_object_reader_repository
    ),
    tp_updater: TemplateParameterUpdater = Depends(
        get_template_parameter_updater_repository
    ),
    tprm_validator: ParameterValidationInteractor = Depends(
        get_template_parameter_validator_interactor
    ),
) -> TemplateParameterUpdaterInteractor:
    return TemplateParameterUpdaterInteractor(
        tp_reader=tp_reader,
        to_reader=to_reader,
        tp_updater=tp_updater,
        tprm_validator=tprm_validator,
        uow=uow,
    )


def bulk_update_template_parameter_interactor(
    uow: UoW = Depends(get_unit_of_work),
    tp_reader: TemplateParameterReader = Depends(
        get_template_parameter_reader_repository
    ),
    to_reader: TemplateObjectReader = Depends(
        get_template_object_reader_repository
    ),
    tp_updater: TemplateParameterUpdater = Depends(
        get_template_parameter_updater_repository
    ),
    tprm_validator: ParameterValidationInteractor = Depends(
        get_template_parameter_validator_interactor
    ),
) -> BulkTemplateParameterUpdaterInteractor:
    return BulkTemplateParameterUpdaterInteractor(
        tp_reader=tp_reader,
        to_reader=to_reader,
        tp_updater=tp_updater,
        tprm_validator=tprm_validator,
        uow=uow,
    )
