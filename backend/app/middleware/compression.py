"""Compress large owner-scoped data payloads, not login/token responses or files."""

from starlette.middleware.gzip import GZipMiddleware


class WorkspaceCompression:
    def __init__(self, app, api_prefix="/api/v1"):
        self.app = app
        self.prefix = api_prefix
        self.compressed = GZipMiddleware(app, minimum_size=1024, compresslevel=4)

    async def __call__(self, scope, receive, send):
        path = scope.get("path", "")
        compress = scope["type"] == "http" and (
            path.startswith(self.prefix + "/jobs/")
            or (
                path.startswith(self.prefix + "/resumes/")
                and path.endswith("/analysis")
            )
        )
        await (self.compressed if compress else self.app)(scope, receive, send)
