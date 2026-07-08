class ApiVersionAliasMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope.get("type") == "http":
            path = scope.get("path", "")
            if path.startswith("/api/v1/"):
                scope = dict(scope)
                scope["path"] = "/api/" + path.removeprefix("/api/v1/")
        await self.app(scope, receive, send)
