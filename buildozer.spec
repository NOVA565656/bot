[app]
title = TikTok Bot
package.name = tiktokbot
package.domain = com.nova
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,html,txt,json
version = 1.0.0

# 🔒 CRITICAL: Pin Cython to a known stable version for p4a
# and use the older OpenAI version that doesn't need Rust
requirements = python3,kivy==2.3.0,cython==0.29.36,requests,python-dotenv,schedule,colorama,openai==0.28.1

orientation = portrait
android.permissions = INTERNET

# Android SDK/NDK settings
android.api = 33
android.minapi = 21
android.ndk_api = 24

# 🔒 CRITICAL: Force the stable NDK (r25b) that p4a is tested against
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.build_tools_version = 33.0.2
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1

# Optional: Try switching to the develop branch of p4a if master is failing
# p4a.branch = develop