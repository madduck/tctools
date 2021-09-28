draws.html schedule.html: tc2web.py ../tc-export-fixed.xls schedule.j2 draws.j2
	./tc2web.py ../tc-export-fixed.xls

../%-fixed.xls: ../%.xls
	../fix-tc-export.sh $<

.PHONY: view clean upload
view: schedule.html
	x-www-browser $<

clean:
	rm -f schedule.html draws.html

upload: draws.html schedule.html
	./upload.sh

tc2web.zip: tc2web.py schedule.j2 draws.j2 display.html index.html display.css style.css
	zip $@ $^
