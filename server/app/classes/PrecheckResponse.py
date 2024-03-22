class PrecheckResponse(Exception):
    def __init__(self, success: bool, reason: str = None, *args, **kwargs) -> None:
        """
        Initializes a new PrecheckResponse instance.

        Args:
            success (bool): Whether the precheck was successful.
            reason (str): Reason for the precheck failure.
        """

        super().__init__(*args, **kwargs)
        self.success = success
        self.reason = reason
