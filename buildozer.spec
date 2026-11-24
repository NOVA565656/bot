[app]
title = TikTok Bot
package.name = tiktokbot
package.domain = com.nova
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,html,txt,json
version = 1.0.0

# BUG FIX 1: Pinned openai to an older version that doesn't require Rust to compile
requirements = python3,kivy,requests,openai==0.28.1,python-dotenv,schedule,colorama

orientation = portrait
android.permissions = INTERNET

# Android SDK settings
android.api = 33
android.minapi = 21

# BUG FIX 2: Added ndk_api to prevent compilation crashes
android.ndk_api = 24

android.archs = arm64-v8a, armeabi-v7a

# BUG FIX 3: Moved build_tools_version into the [app] section where it belongs
android.build_tools_version = 33.0.2

# BUG FIX 4: Automatically accept licenses so the build doesn't pause
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1