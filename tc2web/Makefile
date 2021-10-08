live.html: tc2web.py ../tc-export-demo.xls live.j2
	./rebuild.sh

.PHONY: view clean upload
view: live.html
	x-www-browser $<

clean:
	rm -f live.html

upload: $(wildcard *.html *.css)
	./upload.sh

tc2web.zip: tc2web.py live.j2 display.html index.html display.css style.css
	zip $@ $^
