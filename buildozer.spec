[app]
title = TikTok Bot
package.name = tiktokbot
package.domain = com.nova
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,html,txt,css,js
version = 1.0.0
requirements = python3,flask,flask-cors,openai,python-dotenv,requests,schedule,colorama,sqlite3,pyjnius
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.arch = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1