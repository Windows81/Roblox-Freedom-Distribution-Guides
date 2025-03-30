Rōblox loads some assets from the internet. Many have numeric idens and can only be reached when you're authenticated on Roblox.com.

Let's download them.

---

What assets do we download? Let's find out.

Some files which contain important character scripts are encoded in `rbxm` files. But the `rbxm` format has built-in compression support. Oh. And most `rbxm` files in existence are pre-compressed. To decompress them, you can use RFD to modify them **in-place**:

```ps1
Get-ChildItem -Recurse -Filter *.rbxm |% {
  RFD.exe serialise --method rbxl --load ($_.FullName) --save ($_.FullName)
}
```

Because the files are now decompressed, it's much easier to extract plaintext strings in `rbxm` files, just as it is for non-`rbxm` files.

```ps1
foreach ($p in ('player', 'server')) {
  foreach ($i in (348, 463)) {
    grep --only-matching --no-filename --perl-regexp "(?<=rbxassetid://)[0-9]\{6,\}" -R .\Roblox\v$i\$p\Content\ | Sort-Object -Unique > "./Guides/ExtractingRōbloxAssets/$i-$p.txt"
  }
}
```

_Plenty._

---

Download the files (this command works only if you're before 2025-04-02):

````ps1
cat "./Guides/ExtractingRōbloxAssets/*.txt" | Sort-Object -Unique |% {curl -L "https://assetdelivery.roblox.com/v1/asset/?id=$_" --output ./cache/$_}
```

Rōblox will return _some_ (not all) file data as `gzip`-compressed. How about fixing that?

```ps1
Get-ChildItem "./Guides/ExtractingRōbloxAssets/cache/*" |% {
  $n = $_.FullName
  if ((Get-Content $n -AsByteStream -TotalCount 2) -join ' ' -eq "31 139") {
    mv $n "$n.gz"
    gzip -d "$n.gz"
  }
}
````

---

But some of these files reference other files. Let's decompress them as well:

```ps1
Get-ChildItem "./Guides/ExtractingRōbloxAssets/cache/*" |% {
  RFD.exe serialise --method rbxl --load ($_.FullName) --save ($_.FullName)
}
```

It's gonna take a while...

Then:

```
grep --only-matching --no-filename --perl-regexp "[1-9][0-9]\{6,15\}" --text -R .\cache\ | Sort-Object -Unique > ".\cache.txt"
```
