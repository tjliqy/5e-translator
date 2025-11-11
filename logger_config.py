import logging
import logging.config
from pathlib import Path
from datetime import datetime

# 确保日志目录存在
LOG_DIR = Path("log")
LOG_DIR.mkdir(exist_ok=True)

logging_file_name = f"_{datetime.now().strftime('%Y%m%d%H%M%S')}.log"

# 日志配置字典
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,  # 不关闭已存在的 logger
    "formatters": {
        # 详细格式（用于文件）
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        # 简单格式（用于控制台）
        "simple": {
            "format": "%(levelname)s - %(message)s"
        }
    },
    "handlers": {
        # 控制台处理器（输出 INFO 及以上级别）
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "simple"
        },
        # 文件处理器（输出 DEBUG 及以上级别，全量日志）
        "file_all": {
            "class": "logging.handlers.RotatingFileHandler",  # 按大小轮转
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": LOG_DIR / f"app{logging_file_name}",
            "maxBytes": 1024 * 1024 * 5,  # 单个文件最大 5MB
            "backupCount": 5,  # 保留 5 个备份
            "encoding": "utf-8"
        },
        # 错误日志处理器（仅输出 ERROR 及以上级别）
        "file_error": {
            "class": "logging.handlers.TimedRotatingFileHandler",  # 按时间轮转（每天）
            "level": "ERROR",
            "formatter": "detailed",
            "filename": LOG_DIR / f"error{logging_file_name}",
            "when": "D",  # 每天轮转
            "backupCount": 30,  # 保留 30 天
            "encoding": "utf-8"
        }
    },
    "loggers": {
        # 应用主 logger（默认使用）
        "app": {
            "level": "DEBUG",  # 接收 DEBUG 及以上级别
            "handlers": ["console", "file_all", "file_error"],  # 关联的处理器
            "propagate": False  # 不向上传播（避免重复日志）
        }
    }
}

# 加载配置
logging.config.dictConfig(LOGGING_CONFIG)

# 获取 logger
logger = logging.getLogger("app")

# 使用示例
# logger.debug("这是调试信息（开发环境可见）")
# logger.info("服务启动成功")
# logger.warning("内存使用率超过 80%")
# try:
#     1 / 0
# except ZeroDivisionError:
#     logger.error("除法错误", exc_info=True)  # 手动记录异常堆栈
#     # 或用 logger.exception（自动包含 exc_info=True）
#     logger.exception("发生异常")
# logger.critical("数据库连接失败，服务终止")