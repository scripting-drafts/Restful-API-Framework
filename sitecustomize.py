import warnings

warnings.filterwarnings(
    "ignore",
    message=r"You seem to already have a custom sys\.excepthook handler installed.*",
    category=RuntimeWarning,
)

try:
    import urllib3.util as _util
    from urllib3.util.ssl_ import create_urllib3_context as _ctx
    if not hasattr(_util, "create_urllib3_context"):
        setattr(_util, "create_urllib3_context", _ctx)
except Exception:
    pass
