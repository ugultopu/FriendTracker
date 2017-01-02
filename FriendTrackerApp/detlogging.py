import logging
from pprint import pformat

class _CustomAdapter(logging.LoggerAdapter):
    """
    This example adapter expects the passed in dict-like object to have a
    'connid' key, whose value in brackets is prepended to the log message.
    """
    def process(self, msg, kwargs):
        return pformat(vars(msg)), {'extra': {'omsg': msg}}


def _logger():
    import logging

    border = '---------------------------------------------------------------------------------'
    message = [ border
              , '{pathname} -> {funcName} L:{lineno}'
              , ''
              , '{omsg}'
              , '================================================================================='
              , '{message}'
              , border
              ]
    logger = logging.getLogger('detlogger')
    handler = logging.StreamHandler()
    formatter = logging.Formatter('\n'.join(message), style = '{')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    adapter = _CustomAdapter(logger, '')
    return adapter.debug


detlog = _logger()
