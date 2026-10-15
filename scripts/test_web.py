import urllib.request, urllib.parse, http.cookiejar

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
data = urllib.parse.urlencode({'username': 'admin', 'password': 'admin123'}).encode()
opener.open('http://localhost/honeyguard/login.php', data=data)

decoys_html = opener.open('http://localhost/honeyguard/decoys.php').read().decode('utf-8', errors='replace')
print("col-id in decoys:", 'class="col-id"' in decoys_html)
print("size-pill in decoys:", 'class="size-pill"' in decoys_html)
print("hash-pill in decoys:", 'class="hash-pill"' in decoys_html)
print("fmt- badge in decoys:", 'badge fmt-' in decoys_html)
print("badge-mitigated in decoys:", 'class="badge badge-mitigated"' in decoys_html)

file_mon_html = opener.open('http://localhost/honeyguard/file_monitor.php').read().decode('utf-8', errors='replace')
print("pid-pill in file_monitor:", 'class="pid-pill"' in file_mon_html)

bench_html = opener.open('http://localhost/honeyguard/benchmarks.php').read().decode('utf-8', errors='replace')
print("col-id in benchmarks:", 'class="col-id"' in bench_html)
