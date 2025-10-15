from __future__ import annotations

from framework.app_factory import create_app
from resources import api as api_router

app = create_app()

# (optional) add middlewares here

# include all routers
app.include_router(api_router)

# ---------- ADD THIS ----------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )