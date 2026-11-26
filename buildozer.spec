[app]
title = TikTok Bot
# Changed to bypass any old installation conflicts
package.name = tiktokbot2 
package.domain = com.nova
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,html,txt,json
version = 1.0.0

# Keep these! They fixed the build.
requirements = python3==3.11.16,hostpython3==3.11.16,kivy==2.3.1,cython==3.0.12,requests,python-dotenv,schedule,colorama

orientation = portrait
android.permissions = INTERNET

# Android SDK/NDK settings
android.api = 33
android.minapi = 21
android.ndk_api = 21
android.ndk = 25b

# FIXED: Building for BOTH 32-bit and 64-bit phones
android.archs = arm64-v8a, armeabi-v7a 

android.build_tools_version = 33.0.2
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1