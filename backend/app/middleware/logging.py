import logging
import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("major_compass")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        # 生成本次请求的唯一 ID
        request_id = str(uuid.uuid4())

        # 记录请求开始时间
        start = time.perf_counter()

        # 把 request_id 挂在 request.state 上，路由函数需要时可以读取
        request.state.request_id = request_id

        # call_next 就是"把请求交给下一层处理"（路由函数）
        response: Response = await call_next(request)

        # 路由函数执行完毕，计算耗时
        duration_ms = round((time.perf_counter() - start) * 1000, 2)

        # 写一行结构化日志
        logger.info(
            "%s %s → %s  %.2fms  req=%s",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
            request_id,
        )

        # 把 request_id 加进响应头，前端/运维可以用它追踪问题
        response.headers["X-Request-ID"] = request_id

        return response
