#!/bin/bash
# Optimised for VisualPlugin's personal use on DESKTOP-0676767

# To install the `patch1337` tool, run:
# pip install git+https://github.com/Windows81/Patch1337-Fork.git

cd "$(dirname "$0")" || exit


process() {
	# NOTE: ${2,,} indicates that argument 2 is made lowercase.
	haxdiff d "../../../Roblox/${1}/${2}/_${3}__very_original.exe" "../../../Roblox/${1}/${2}/${3}.exe" >"${1}-${2,,}.haxdiff"
	cp -f "../../../Roblox/${1}/${2}/_${3}__very_original.exe" "../../../Roblox/${1}/${2}/_${3}__quite_patched.exe"
	find -D exec "../../" -name "${1}-${2,,}.1337" -type f -exec patch1337 -t "../../../Roblox/${1}/${2}/_${3}__quite_patched.exe" -p "{}" --ignore_target_name --skip_backup --normal_only \;
	haxdiff d "../../../Roblox/${1}/${2}/_${3}__quite_patched.exe" "../../../Roblox/${1}/${2}/${3}.exe" >"${1}-${2,,}-remaining.haxdiff"
}

process "v347" "Player" "RobloxPlayerBeta"
process "v463" "Player" "RobloxPlayerBeta"

process "v347" "Server" "RCCService"
process "v463" "Server" "RCCService"

process "v347" "Studio" "RobloxStudioBeta"
process "v463" "Studio" "RobloxStudioBeta"
