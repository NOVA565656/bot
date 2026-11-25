[app]
title = TikTok Bot
package.name = tiktokbot
package.domain = com.nova
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,html,txt,json
version = 1.0.0

# ✅ CORRECT PINNING: This forces Python 3.11 and uses a compatible Cython.
# This is the official syntax for python-for-android.
requirements = python3==3.11.16,hostpython3==3.11.16,kivy==2.3.0,cython==3.0.12,requests,python-dotenv,schedule,colorama,openai==0.28.1

orientation = portrait
android.permissions = INTERNET

# Android SDK/NDK settings
android.api = 33
android.minapi = 21
android.ndk_api = 24
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.build_tools_version = 33.0.2
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1