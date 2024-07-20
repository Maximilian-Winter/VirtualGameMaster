[app]
title = RPG App
package.name = rpgapp
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy,requests,pyyaml,python-dotenv,openai

# (list) Permissions
android.permissions = INTERNET

# (str) Supported orientation (one of portrait, landscape, or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

[buildozer]
# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (str) Path to build artifact storage, absolute or relative to spec file
build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .ipa) storage
bin_dir = ./bin

android.sdk_path = /mnt/c/Users/maxim/AppData/Local/Android/Sdk