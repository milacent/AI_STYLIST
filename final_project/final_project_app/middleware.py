import logging

log = logging.getLogger('final_project_app')

class ErrorLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code >= 400:
            log.error(f"{response.status_code} error at {request.path}")
        return response
