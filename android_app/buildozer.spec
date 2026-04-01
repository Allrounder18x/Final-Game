[app]
title = Cricket Cap Cum Coach
package.name = cricketcapcumcoach
package.domain = org.cricket.manager
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,pkl,txt
version = 0.1.0
# Host Cython must stay <3.1 until pyjnius drops `long` in .pxi (CI/Codemagic pip pins this).
requirements = python3,kivy,kivymd
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 24
android.archs = arm64-v8a,armeabi-v7a
android.ndk = 25b
log_level = 2

[buildozer]
log_level = 2
warn_on_root = 1
