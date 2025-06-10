from fastapi import FastAPI

from common.core.exception_handle import register_exception_handlers


def init_exception_handler(app: FastAPI):
    register_exception_handlers(app)