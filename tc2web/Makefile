live.html: tc2web.py ../tc-export-demo.xls ../tc-export-fixed.xls live.j2
	./rebuild.sh

.PHONY: view clean upload
view: live.html
	x-www-browser $<

clean:
	rm -f live.html .shasums

upload: $(wildcard *.html *.css)
	./upload.sh

../tc-export-fixed.xls: ../tc-export.xls
	../fix-tc-export.sh

tc2web.zip: tc2web.py live.j2 display.html index.html display.css style.css
	zip $@ $^
