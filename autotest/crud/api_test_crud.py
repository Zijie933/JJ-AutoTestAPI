from sqlalchemy import select
from sqlalchemy.orm import Session

from autotest.schemas.api_test_schemas import ApiTestCaseCreate, ApiTestCaseUpdate
from common.models.api_test import ApiTestCase, ApiTestCaseRunModel


def save_api_test(*, db: Session, test_in: ApiTestCaseCreate):
    api_test_case = ApiTestCase.model_validate(
        test_in, update={"id": None, "method": test_in.method.upper()}
    )
    db.add(api_test_case)
    db.commit()
    db.refresh(api_test_case)
    return api_test_case

def get_api_test_by_id(*, db: Session, test_id: int):
    api_test_case = db.get(ApiTestCase, test_id)
    return api_test_case

def get_api_test_by_name(*, db: Session, test_name: str):
    stmt = select(ApiTestCase).where(ApiTestCase.name == test_name)
    api_test_case = db.exec(stmt).first()
    return api_test_case

# 更新
def update_api_test(*, db: Session, test_in: ApiTestCaseUpdate):
    case = db.get(ApiTestCase, test_in.id)
    if not case:
        return None

    if test_in.name is not None:
        case.name = test_in.name
    if test_in.url is not None:
        case.url = test_in.url
    if test_in.method is not None:
        case.method = test_in.method.upper()
    if test_in.headers is not None:
        case.headers = test_in.headers
    if test_in.body is not None:
        case.body = test_in.body
    if test_in.params is not None:
        case.params = test_in.params
    if test_in.cookies is not None:
        case.cookies = test_in.cookies


    db.add(case)
    db.commit()
    db.refresh(case)

    return case


def get_api_test_list(*, db: Session):
    results = db.query(ApiTestCase).all()
    return results


def delete_api_test(*, db: Session, test_id: int):
    api_test_case = db.get(ApiTestCase, test_id)
    if not api_test_case:
        return False
    db.delete(api_test_case)
    db.commit()
    return True
