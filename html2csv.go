// Converts HSBCnet's Excel export, which is actually HTML, into CSV format.
package main

import (
	"errors"
	"fmt"
	"io/ioutil"
	"os"
	"regexp"
	"strings"
)

var tableStart = regexp.MustCompile(`<table[^>]*>`)
var tableEnd = regexp.MustCompile(`</table[^>]*>`)
var trStart = regexp.MustCompile(`<tr[^>]*>`)
var trEnd = regexp.MustCompile(`</tr[^>]*>`)
var tdStart = regexp.MustCompile(`<td[^>]*>`)
var tdEnd = regexp.MustCompile(`</td[^>]*>`)
var spanStart = regexp.MustCompile(`<span[^>]*>`)
var spanEnd = regexp.MustCompile(`</span[^>]*>`)

var noStartTag = errors.New("no start tag found")
var noEndTag = errors.New("no end tag found")

type tagOffsets struct {
	startTag [2]int
	endTag   [2]int
}

func (t *tagOffsets) content(data []byte) []byte {
	return data[t.startTag[1]:t.endTag[0]]
}

func (t *tagOffsets) after(data []byte) []byte {
	return data[t.endTag[1]:len(data)]
}

func findTag(data []byte, tagStart *regexp.Regexp, tagEnd *regexp.Regexp) (tagOffsets, error) {
	start := tagStart.FindIndex(data)
	if start == nil {
		return tagOffsets{}, noStartTag
	}
	end := tagEnd.FindIndex(data[start[1]:len(data)])
	if end == nil {
		return tagOffsets{}, noEndTag
	}
	end[0] += start[1]
	end[1] += start[1]
	return tagOffsets{
		[2]int{start[0], start[1]},
		[2]int{end[0], end[1]},
	}, nil
}

func stripSpan(data []byte) []byte {
	span, err := findTag(data, spanStart, spanEnd)
	if err != nil {
		if err != noStartTag {
			panic(err)
		}
		return data
	}
	return span.content(data)
}

func main() {
	if len(os.Args) != 2 {
		fmt.Fprintf(os.Stderr, "html2csv (input file)\n")
		os.Exit(1)
	}
	path := os.Args[1]

	contents, err := ioutil.ReadFile(path)
	if err != nil {
		panic(err)
	}

	table, err := findTag(contents, tableStart, tableEnd)
	if err != nil {
		panic(err)
	}
	contents = table.content(contents)
	for {
		tr, err := findTag(contents, trStart, trEnd)
		if err != nil {
			if err != noStartTag {
				panic(err)
			}
			break
		}

		trContent := tr.content(contents)
		firstCell := true
		for {
			td, err := findTag(trContent, tdStart, tdEnd)
			if err != nil {
				if err != noStartTag {
					panic(err)
				}
				break
			}
			cellData := string(stripSpan(td.content(trContent)))
			cellData = strings.TrimSpace(cellData)
			if strings.Contains(cellData, ",") {
				cellData = `"` + cellData + `"`
			}

			if firstCell {
				firstCell = false
			} else {
				os.Stdout.Write([]byte(","))
			}
			os.Stdout.WriteString(cellData)
			trContent = td.after(trContent)
		}
		os.Stdout.Write([]byte("\n"))
		contents = tr.after(contents)
	}
}
