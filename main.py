from pathlib import Path
import logger

def init_logging(level=None, path=None):
    if level is not None:
        log_level = level
    else:
        log_level = "INFO"
    return logger.init(log_level, path)



if __name__ == "__main__":
    log_path = Path("logs")
    log_path.mkdir(parents=True, exist_ok=True)
    main_log_path = log_path / "hyperview.logs"
    main_log_path.touch(exist_ok=True)
    main_logger = init_logging(args.log_level, str(main_log_path.resolve()))
    # SET AUDIT LOGGER
    audit_log_path = log_path / "audit.logs"
    audit_log_path.touch(exist_ok=True)
    audit_logger = logger.audit_init('audit_logger', audit_log_path)
    # SET MIGRATION LOGGER
    migration_log_path = log_path / "migration.logs"
    migration_log_path.touch(exist_ok=True)
    migration_logger = logger.migration_init('migration_logger', migration_log_path)
