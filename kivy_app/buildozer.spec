[app]
title = Aprenda+
package.name = aprendamais
package.domain = br.erikrib

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
source.include_patterns = data/*.json

version = 1.0.0

requirements = python3==3.11,kivy==2.2.1,kivymd==1.1.1,pillow

orientation = portrait
fullscreen = 0

android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.accept_sdk_license = True
android.arch = arm64-v8a

[buildozer]
log_level = 2
