"""
utils/check_settings_import.py

AutoSearch V4

Settings Import Diagnostic

用途：

確認 Python 實際載入的 config.settings
是否為目前 AutoSearch V4 的設定模組。
"""

import crawler.settings as settings

def main():
    print("=" * 60)
    print("AutoSearch V4 Settings Diagnostic")
    print("=" * 60)

    print()
    print("settings module:")
    print(settings)

    print()
    print("settings file:")
    print(getattr(settings, "__file__", None))

    print()
    print("settings package:")
    print(getattr(settings, "__package__", None))

    print()
    print("settings name:")
    print(getattr(settings, "__name__", None))

    print()
    print("APP_NAME:")
    print(getattr(settings, "APP_NAME", "<MISSING>"))

    print()
    print("APP_VERSION:")
    print(getattr(settings, "APP_VERSION", "<MISSING>"))

    print()
    print("APP_ENV:")
    print(getattr(settings, "APP_ENV", "<MISSING>"))

    print()
    print("CRAWL_DELAY:")
    print(getattr(settings, "CRAWL_DELAY", "<MISSING>"))

    print()
    print("DATABASE_HOST:")
    print(getattr(settings, "DATABASE_HOST", "<MISSING>"))

    print()
    print("AI_ENABLED:")
    print(getattr(settings, "AI_ENABLED", "<MISSING>"))

    print()
    print("__all__:")
    print(getattr(settings, "__all__", "<MISSING>"))

    print()
    print("=" * 60)


if __name__ == "__main__":
    main()