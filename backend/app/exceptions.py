import uuid


class MajorCompassError(Exception):
    """所有业务异常的基类，方便统一捕获。"""
    pass


class SessionNotFoundError(MajorCompassError):
    def __init__(self, session_id: uuid.UUID):
        self.session_id = session_id
        super().__init__(f"Session {session_id} not found.")


class SessionAbandonedError(MajorCompassError):
    def __init__(self, session_id: uuid.UUID):
        self.session_id = session_id
        super().__init__(f"Session {session_id} has been abandoned.")


class SessionAlreadyCompletedError(MajorCompassError):
    def __init__(self, session_id: uuid.UUID):
        self.session_id = session_id
        super().__init__(f"Session {session_id} is already completed.")


class InsufficientResponsesError(MajorCompassError):
    def __init__(self, answered: int, required: int):
        self.answered = answered
        self.required = required
        super().__init__(f"Only {answered}/{required} questions answered.")