from threading import local

_thread_locals = local()


def set_current_company(company):
    _thread_locals.company = company


def get_current_company():
    return getattr(_thread_locals, "company", None)


def set_current_user(user):
    _thread_locals.user = user


def get_current_user():
    return getattr(_thread_locals, "user", None)


def set_current_ip(ip):
    _thread_locals.ip = ip


def get_current_ip():
    return getattr(_thread_locals, "ip", None)
