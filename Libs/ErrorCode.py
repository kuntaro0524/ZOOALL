from enum import Enum

class ErrorCode(Enum):
    # SPACE warnings
    SPACE_WARNING_SUSPECTED = 9001  # 存在が疑われるもの
    SPACE_WARNING_LHEAD_PUSHED = 9002  # Lheadが過剰に押された場合
    SPACE_WARNING_ROTATE_TOO_MUCH = 9003  # ヘッドが掴めなかった系
    SPACE_WARNING_GRAB_FAILED = 9004  # つかみとり失敗

    # SPACE accidents
    SPACE_ACCIDENT_LHEAD_PULLED = 9997  # Lheadが引っ張られた
    SPACE_UNKNOWN_ACCIDENT = 9998  # 上記以外の未知の事故
    SPACE_ACCIDENT = 9999  # SPACEアクシデント

    # センタリングの失敗
    CENTERING_FAILURE = 1001

    # ラスタースキャンエラー
    RASTER_SCAN_FAILURE_MEASUREMENT = 2001  # ラスタースキャン中の測定失敗
    RASTER_SCAN_FAILURE_ANALYSIS = 2002  # ラスタースキャンの解析失敗
    RASTER_SCAN_NO_CRYSTAL = 2003  # ラスタースキャンで結晶がなかった
    RASTER_SCAN_UNKNOWN_ERROR = 2004 # ラスタースキャン中の未知のエラー

    # データ測定エラー
    DATA_COLLECTION_FAILURE = 3001  # データ測定中の失敗
    DATA_COLLECTION_NO_CRYSTAL = 3002  # 測定の結晶が見つからなかった
    DATA_COLLECTION_UNKNOWN_ERROR = 3003

    # Beam dump error
    BEAM_DUMP_RECOVERED = 4001  # ビームダンプからの復旧

    # 測定モードエラー
    UNKNOWN_MEASUREMENT_MODE = 8001  # 測定モード不明エラー

    # 未知のエラー
    UNKNOWN_ERROR = -1  # デフォルトの未知エラー

    # success
    SUCCESS = 1

    NOT_PROCESSED = 0 # 未処理

    @classmethod
    def from_code(cls, code: int):
        """ エラーコード (int) から対応する Enum を取得 """
        return cls._value2member_map_.get(code, cls.UNKNOWN_ERROR)

    def description(self) -> str:
        """ Return the error description in English """
        descriptions = {
            self.SPACE_WARNING_SUSPECTED: "SPACE warning: Suspected existence",
            self.SPACE_WARNING_LHEAD_PUSHED: "SPACE warning: Lhead pushed too much",
            self.SPACE_WARNING_ROTATE_TOO_MUCH: "SPACE warning: Thead: Rotate too much",
            self.SPACE_ACCIDENT_LHEAD_PULLED: "SPACE accident: Lhead was pulled by UniPuck",
            self.SPACE_UNKNOWN_ACCIDENT: "SPACE accident: Unknown accident (requires classification: contact K. Hirata)",
            self.SPACE_ACCIDENT: "SPACE accident occurred",
            self.CENTERING_FAILURE: "Centering failed",
            self.SPACE_WARNING_GRAB_FAILED: "SPACE warning: Grub failed to pick up the sample pin",
            self.RASTER_SCAN_FAILURE_MEASUREMENT: "Raster scan failed during measurement",
            self.RASTER_SCAN_FAILURE_ANALYSIS: "Raster scan failed during analysis",
            self.RASTER_SCAN_NO_CRYSTAL: "No crystal found after raster scan",
            self.RASTER_SCAN_UNKNOWN_ERROR: "Unknown error occurred during raster scan",
            self.DATA_COLLECTION_FAILURE: "Data collection failed.",
            self.DATA_COLLECTION_NO_CRYSTAL: "No crystal found for data collection",
            self.DATA_COLLECTION_UNKNOWN_ERROR: "Unknown error occurred during data collection",
            self.UNKNOWN_MEASUREMENT_MODE: "Unknown measurement mode",
            self.UNKNOWN_ERROR: "Unknown error",
            self.BEAM_DUMP_RECOVERED: "Beam dump recovered",
            self.SUCCESS: "Success"
        }
        return descriptions.get(self, "Undefined error")

    def to_db_value(self) -> int:
        """ データベースに格納するための数値を取得 """
        return self.value

    @classmethod
    def getMessage(cls, code):
        """
        int または ErrorCode を受け取り、
        meas_record 用の文字列を返す
        """
        if isinstance(code, int):
            code = cls.from_code(code)
    
        if isinstance(code, cls):
            return code.description()
    
        return f"Unknown error (code={code})"

# mainが定義されていなかったら実行
if __name__ == "__main__":
    test_values = [
        ErrorCode.SPACE_ACCIDENT,
        ErrorCode.SPACE_ACCIDENT.to_db_value(),
        2001,
        1001,
        -1,
        3001
    ]

    for value in test_values:
        print(value, "->", ErrorCode.getMessage(value))