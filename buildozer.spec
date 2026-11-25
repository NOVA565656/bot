[app]
title = TikTok Bot
package.name = tiktokbot
package.domain = com.nova
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,html,txt,json
version = 1.0.0

# ✅ Kept all pins! Added tiktoksigner at the end.
requirements = python3==3.11.16,hostpython3==3.11.16,kivy==2.3.1,cython==3.0.12,requests,python-dotenv,schedule,colorama,openai==0.28.1,tiktoksigner

orientation = portrait
android.permissions = INTERNET

# Android SDK/NDK settings (Matches Android 9 and modern compile requirements)
android.api = 33
android.minapi = 21
android.ndk_api = 21
android.ndk = 25b

android.archs = arm64-v8a 
android.build_tools_version = 33.0.2
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1