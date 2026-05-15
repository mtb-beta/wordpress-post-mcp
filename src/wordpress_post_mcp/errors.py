class WordPressMCPError(Exception):
    """WordPress MCP サーバーの基底例外クラス。"""


class ConfigurationError(WordPressMCPError):
    """環境変数や設定ファイルの不備。"""


class WordPressAPIError(WordPressMCPError):
    """WordPress REST API が非 2xx を返した。"""

    def __init__(self, message: str, status_code: int) -> None:
        super().__init__(message)
        self.status_code = status_code


class NetworkError(WordPressMCPError):
    """WordPress への接続に失敗した。"""
