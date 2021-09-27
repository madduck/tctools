tc-export-fixed.xls: tc-export.xls
	libreoffice --convert-to ods $<
	mv $(basename $<).ods $(basename $@).ods
	libreoffice --convert-to xls $(basename $@).ods
	rm $(basename $@).ods

.PHONY: clean
clean:
	rm -f tc-export-fixed.xls
