[app]

# (str) Title of your application
title = MyDays

# (str) Package name
package.name = mydays

# (str) Package domain (needed for android/ios packaging)
package.domain = org.mycompany

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,ttf


# (str) Application versioning
version = 0.1

# (list) Application requirements
requirements = python3,kivy,pillow,pyttsx3,requests,certifi,pyjnius

# (list) Supported orientations
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET, ACCESS_NETWORK_STATE, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, CAMERA, ACCESS_FINE_LOCATION

# (int) Target Android API
android.api = 31

# (int) Minimum API your APK will support
android.minapi = 21

# (bool) Accept SDK license
android.accept_sdk_license = True

# (list) Supported Android architectures
android.archs = arm64-v8a, armeabi-v7a

# (bool) Enables Android auto backup
android.allow_backup = True

# (int) Log verbosity (0 = quiet, 2 = verbose)
android.log_level = 2

# ✅ 非常关键：排除所有不相关目录，避免 Steam、Unity、OBS 等目录误打包
source.exclude_dirs = .git,__pycache__,.venv,Library,build,.buildozer,Applications,Documents,Downloads

